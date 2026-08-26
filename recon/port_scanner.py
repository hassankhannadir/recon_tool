"""Lightweight TCP port scanning for a user-supplied host or domain."""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import socket
from typing import Iterable, List, Sequence

DEFAULT_PORTS = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3389, 8080, 8443]

_DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$"
)


def validate_target(target: str) -> str:
    """Normalize a hostname or IP provided by the user."""
    if not isinstance(target, str):
        raise ValueError("Target must be a string.")

    cleaned = target.strip().lower().rstrip(".")
    if not cleaned:
        raise ValueError("Target cannot be empty.")

    if cleaned.startswith(("http://", "https://")):
        cleaned = cleaned.split("//", 1)[1]

    cleaned = cleaned.split("/", 1)[0]

    try:
        ipaddress.ip_address(cleaned)
        return cleaned
    except ValueError:
        pass

    if not _DOMAIN_PATTERN.match(cleaned):
        raise ValueError(f"Invalid target: {target!r}")

    return cleaned


def _parse_ports(raw_ports: Sequence[int] | str | None) -> List[int]:
    """Convert supported port input styles into a flat list of integers."""
    if raw_ports is None:
        return DEFAULT_PORTS[:]

    if isinstance(raw_ports, (int, str)):
        raw_ports = [raw_ports]

    ports: List[int] = []
    for entry in raw_ports:
        if isinstance(entry, str):
            value = entry.strip()
            if not value:
                continue
            if "-" in value:
                start_text, end_text = value.split("-", 1)
                try:
                    start = int(start_text)
                    end = int(end_text)
                except ValueError as exc:
                    raise ValueError(f"Invalid port range: {value!r}") from exc
                if start > end:
                    start, end = end, start
                ports.extend(range(start, end + 1))
            else:
                try:
                    ports.append(int(value))
                except ValueError as exc:
                    raise ValueError(f"Invalid port value: {value!r}") from exc
        else:
            ports.append(int(entry))

    normalized = []
    seen = set()
    for port in ports:
        if 1 <= port <= 65535 and port not in seen:
            normalized.append(port)
            seen.add(port)

    return normalized


def scan_ports(target: str, ports: Sequence[int] | str | None = None, timeout: float = 1.0) -> dict:
    """Scan a target for open TCP ports and return a structured summary."""
    normalized = validate_target(target)
    port_list = _parse_ports(ports)

    if not port_list:
        raise ValueError("No valid ports were provided to scan.")

    open_ports: List[int] = []
    filtered_ports: List[int] = []
    errors: List[str] = []

    try:
        address_info = socket.getaddrinfo(normalized, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise RuntimeError(f"DNS resolution failed for {normalized}: {exc}") from exc

    resolved_hosts = []
    for family, _, _, _, sockaddr in address_info:
        if sockaddr and sockaddr[0] not in resolved_hosts:
            resolved_hosts.append(sockaddr[0])

    if not resolved_hosts:
        raise RuntimeError(f"No IP addresses were resolved for {normalized}.")

    for port in port_list:
        for host in resolved_hosts:
            try:
                with socket.create_connection((host, port), timeout=timeout):
                    open_ports.append(port)
                    break
            except (socket.timeout, TimeoutError, OSError):
                pass
            except Exception as exc:  # pragma: no cover - defensive fallback
                errors.append(f"Port {port}: {exc}")

    for port in port_list:
        if port not in open_ports:
            filtered_ports.append(port)

    return {
        "target": normalized,
        "status": "ok" if open_ports else "no_open_ports",
        "timeout": timeout,
        "open_ports": sorted(open_ports),
        "scanned_ports": sorted(set(port_list)),
        "closed_ports": sorted(set(filtered_ports) - set(open_ports)),
        "errors": errors,
    }


def _prompt_for_target() -> str:
    """Prompt the user for a target when using the script interactively."""
    user_input = input("Enter target: ").strip()
    if not user_input:
        raise ValueError("Target cannot be empty.")
    return user_input


def main(argv: List[str] | None = None) -> int:
    """Simple CLI entry point for quick port scanning."""
    parser = argparse.ArgumentParser(description="Scan a target host for common open TCP ports.")
    parser.add_argument("target", nargs="?", help="Hostname or IP address to scan")
    parser.add_argument("--target", dest="flag_target", help="Hostname or IP address to scan")
    parser.add_argument("--ports", nargs="*", help="Ports or ranges to scan, e.g. 80 443 8080-8081")
    parser.add_argument("--timeout", type=float, default=1.0, help="Socket timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Return JSON instead of text")
    args = parser.parse_args(argv)

    target = args.flag_target or args.target
    if not target:
        try:
            target = _prompt_for_target()
        except EOFError:
            print("No target provided. Exiting.")
            return 1
        except ValueError as exc:
            print(f"Error: {exc}")
            return 1

    try:
        result = scan_ports(target, ports=args.ports, timeout=args.timeout)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}")
        return 1

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Target: {result['target']}")
        print(f"Open ports: {result['open_ports'] if result['open_ports'] else 'None'}")
        if result['errors']:
            print("Errors:")
            for error in result['errors']:
                print(f"  - {error}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
