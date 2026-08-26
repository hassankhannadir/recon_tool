"""WHOIS and DNS helper functions for the reconnaissance toolkit."""

from __future__ import annotations

import argparse
import json
import re
import socket
from typing import Any, Dict, List

try:  # optional dependency
    import dns.resolver  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    dns = None


_DOMAIN_RE = re.compile(
    r"^(?:(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)\.)+[A-Za-z]{2,63}$"
)
_IP_RE = re.compile(r"^(?:\d{1,3}\.){3}\d{1,3}$")


def validate_target(target: str) -> str:
    """Validate a domain name or IP address."""
    if target is None:
        raise ValueError("A target domain or IP is required.")
    cleaned = target.strip().lower().rstrip(".")
    if not cleaned:
        raise ValueError("A target domain or IP is required.")
    if _DOMAIN_RE.match(cleaned) or _IP_RE.match(cleaned):
        return cleaned
    raise ValueError(f"Invalid target: {target}")


def resolve_ip(domain: str) -> Dict[str, Any]:
    """Resolve a hostname to IPv4 addresses."""
    target = validate_target(domain)
    try:
        info = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return {"status": "error", "target": target, "error": str(exc), "ips": []}

    ips = []
    for _, _, _, _, sockaddr in info:
        ip = sockaddr[0]
        if ip not in ips:
            ips.append(ip)
    return {"status": "ok", "target": target, "ips": ips}


def dns_lookup(domain: str) -> Dict[str, Any]:
    """Return a structured DNS summary for a target."""
    target = validate_target(domain)
    records: Dict[str, List[str]] = {"A": [], "MX": [], "TXT": [], "NS": []}

    try:
        info = socket.getaddrinfo(target, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return {"status": "error", "target": target, "error": str(exc), "records": records}

    for _, _, _, _, sockaddr in info:
        ip = sockaddr[0]
        if ip not in records["A"]:
            records["A"].append(ip)

    if dns is not None:
        try:
            resolver = dns.resolver.Resolver()
            for record_type, key in (("MX", "MX"), ("TXT", "TXT"), ("NS", "NS")):
                try:
                    answers = resolver.resolve(target, record_type)
                    records[key] = [str(item).rstrip(".") for item in answers]
                except Exception:
                    continue
        except Exception:
            pass

    return {
        "status": "ok",
        "target": target,
        "records": records,
        "ip_resolution": {"ipv4": records["A"]},
    }


def whois_lookup(domain: str) -> Dict[str, Any]:
    """Query a WHOIS server for the provided domain."""
    target = validate_target(domain)
    server_map = {
        ".com": "whois.verisign-grs.com",
        ".net": "whois.verisign-grs.com",
        ".org": "whois.publicinterestregistry.net",
        ".io": "whois.nic.io",
        ".edu": "whois.educause.edu",
        ".info": "whois.afilias.net",
        ".co": "whois.nic.co",
    }
    server = "whois.iana.org"
    for suffix, candidate in server_map.items():
        if target.endswith(suffix):
            server = candidate
            break

    try:
        with socket.create_connection((server, 43), timeout=5) as sock:
            sock.sendall((target + "\r\n").encode("utf-8"))
            chunks: List[bytes] = []
            for _ in range(20):
                chunk = sock.recv(4096)
                if not chunk:
                    break
                chunks.append(chunk)
                if sum(len(part) for part in chunks) >= 65536:
                    break
    except (OSError, socket.timeout) as exc:
        return {"status": "error", "target": target, "server": server, "error": str(exc)}

    data = b"".join(chunks)
    decoded = data.decode("utf-8", errors="replace")
    return {"status": "ok", "target": target, "server": server, "whois": decoded.strip()}


def main(argv: Any = None) -> int:
    """Run the WHOIS/DNS module directly from the command line."""
    parser = argparse.ArgumentParser(description="WHOIS and DNS reconnaissance")
    parser.add_argument("--domain", help="Domain or IP to inspect")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args(argv)

    domain = args.domain or input("Enter domain: ").strip()
    result = {
        "target": domain,
        "whois": whois_lookup(domain),
        "dns": dns_lookup(domain),
    }

    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
