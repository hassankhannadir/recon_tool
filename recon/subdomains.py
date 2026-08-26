"""Passive subdomain enumeration helpers."""

from __future__ import annotations

import argparse
import json
import re
from typing import Any, Dict, Iterable, List, Set
from urllib import request


_DOMAIN_RE = re.compile(
    r"^(?:(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)\.)+[A-Za-z]{2,63}$"
)


def validate_target(target: str) -> str:
    """Validate a target domain name."""
    if target is None:
        raise ValueError("A target domain is required.")
    cleaned = target.strip().lower().rstrip(".")
    if not cleaned or not _DOMAIN_RE.match(cleaned):
        raise ValueError(f"Invalid target domain: {target}")
    return cleaned


def _iter_values(raw: Any) -> Iterable[str]:
    if raw is None:
        return []
    if isinstance(raw, str):
        return [part.strip() for part in re.split(r"[\r\n,\s]+", raw) if part.strip()]
    if isinstance(raw, list):
        values = []
        for item in raw:
            values.extend(_iter_values(item))
        return values
    if isinstance(raw, dict):
        values = []
        for key, value in raw.items():
            if key in {"name", "name_value", "subdomain", "hostname"}:
                values.extend(_iter_values(value))
            else:
                values.extend(_iter_values(value))
        return values
    return [str(raw)]


def _dedupe(items: Iterable[str], base: str) -> List[str]:
    found: Set[str] = set()
    out: List[str] = []
    for item in items:
        candidate = item.strip().lower().rstrip(".")
        if not candidate or candidate == base:
            continue
        if candidate not in found:
            found.add(candidate)
            out.append(candidate)
    return sorted(out)


def _fetch_text(url: str, timeout: float = 10.0) -> str:
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def _parse_crtsh(raw: str) -> List[str]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    names: List[str] = []
    for item in payload:
        if isinstance(item, dict):
            value = item.get("name_value") or item.get("common_name")
            if isinstance(value, str):
                names.extend(value.split("\n"))
    return names


def _parse_hackertarget(raw: str) -> List[str]:
    return [line.strip() for line in raw.splitlines() if line.strip() and not line.startswith("#")]


def _parse_bufferover(raw: str) -> List[str]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if isinstance(payload, dict):
        return _iter_values(payload.get("Results", payload))
    return _iter_values(payload)


def enumerate_subdomains(domain: str, timeout: float = 10.0) -> Dict[str, Any]:
    """Return a deduplicated set of subdomains for a target domain."""
    target = validate_target(domain)
    lookup_urls = [
        ("crt.sh", f"https://crt.sh/?q=%25.{target}&output=json"),
        ("hackertarget", f"https://api.hackertarget.com/hostsearch/?q={target}"),
        ("bufferover", f"https://dns.bufferover.run/dns?q={target}"),
    ]

    subdomains: List[str] = []
    errors: List[str] = []

    for source, url in lookup_urls:
        try:
            text = _fetch_text(url, timeout=timeout)
            if source == "crt.sh":
                candidates = _parse_crtsh(text)
            elif source == "hackertarget":
                candidates = _parse_hackertarget(text)
            else:
                candidates = _parse_bufferover(text)
            subdomains.extend(candidates)
        except Exception as exc:  # pragma: no cover - network-dependent path
            errors.append(f"{source}: {exc}")

    resolved = _dedupe(subdomains, target)
    status = "ok" if resolved else "no_results"
    return {
        "status": status,
        "target": target,
        "subdomains": resolved,
        "errors": errors,
    }


def main(argv: Any = None) -> int:
    """CLI entry point for subdomain enumeration."""
    parser = argparse.ArgumentParser(description="Passive subdomain enumeration")
    parser.add_argument("--domain", help="Target domain to inspect")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    args = parser.parse_args(argv)

    domain = args.domain or input("Enter domain: ").strip()
    result = enumerate_subdomains(domain)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
