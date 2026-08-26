"""Generate human-readable reconnaissance reports from structured module results."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Union


def _format_section(data: Any) -> str:
    """Return a compact string representation for nested dictionary/list values."""
    if isinstance(data, (dict, list, tuple, set)):
        if not data:
            return "None"
        return str(data)
    if data is None:
        return "None"
    return str(data)


def _normalize_results(results: Dict[str, Any]) -> Dict[str, Any]:
    """Return a report-friendly copy of the structured results."""
    normalized = dict(results or {})
    normalized.setdefault("target", "N/A")
    normalized.setdefault("timestamp", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z"))
    normalized.setdefault("ip_resolution", {})
    normalized.setdefault("whois", {})
    normalized.setdefault("dns", {})
    normalized.setdefault("subdomains", [])
    normalized.setdefault("ports", [])
    normalized.setdefault("banners", {})
    normalized.setdefault("technologies", [])
    return normalized


def generate_report(results: Dict[str, Any]) -> str:
    """Create a plain-text reconnaissance report from structured module data."""
    data = _normalize_results(results)
    target = data.get("target", "N/A")
    timestamp = data.get("timestamp", "N/A")

    ip_resolution = data.get("ip_resolution") or {}
    whois = data.get("whois") or {}
    dns = data.get("dns") or {}
    subdomains = data.get("subdomains") or []
    ports = data.get("ports") or []
    banners = data.get("banners") or {}
    technologies = data.get("technologies") or []

    lines = [
        "========================================",
        "RECONNAISSANCE REPORT",
        "========================================",
        "",
        f"Target: {target}",
        f"Timestamp: {timestamp}",
        "",
        "IP Resolution:",
        f"    IPv4: {_format_section(ip_resolution.get('ipv4', []))}",
        f"    IPv6: {_format_section(ip_resolution.get('ipv6', []))}",
        "",
        "WHOIS:",
        f"    {_format_section(whois)}",
        "",
        "DNS:",
        f"    A: {_format_section(dns.get('records', {}).get('A', []))}",
        f"    MX: {_format_section(dns.get('records', {}).get('MX', []))}",
        f"    TXT: {_format_section(dns.get('records', {}).get('TXT', []))}",
        f"    NS: {_format_section(dns.get('records', {}).get('NS', []))}",
        "",
        "Subdomains:",
        f"    {_format_section(subdomains)}",
        "",
        "Open Ports:",
        f"    {_format_section(ports)}",
        "",
        "Service Banners:",
        f"    {_format_section(banners)}",
        "",
        "Detected Technologies:",
        f"    {_format_section(technologies)}",
        "",
        "========================================",
        "END OF REPORT",
        "========================================",
    ]
    return "\n".join(lines) + "\n"


def generate_html_report(results: Dict[str, Any]) -> str:
    """Create a minimal HTML report for the same structured results."""
    data = _normalize_results(results)
    target = data.get("target", "N/A")
    timestamp = data.get("timestamp", "N/A")
    subdomains = data.get("subdomains") or []
    ports = data.get("ports") or []
    technologies = data.get("technologies") or []
    banners = data.get("banners") or {}

    def fmt(value):
        return "&nbsp;".join(str(item) for item in value) if isinstance(value, list) else str(value)

    html = [
        "<!DOCTYPE html>",
        "<html><head><meta charset='utf-8'><title>Reconnaissance Report</title>",
        "<style>body{font-family:Arial,sans-serif;margin:2rem;}h1{margin-bottom:0.5rem;}table{border-collapse:collapse;width:100%;margin-top:1rem;}td{border:1px solid #ccc;padding:8px;vertical-align:top;}th{background:#f4f4f4;padding:8px;border:1px solid #ccc;text-align:left;}</style>",
        "</head><body>",
        f"<h1>Reconnaissance Report</h1>",
        f"<p><strong>Target:</strong> {target}</p>",
        f"<p><strong>Timestamp:</strong> {timestamp}</p>",
        "<table>",
        "<tr><th>Category</th><th>Value</th></tr>",
        f"<tr><td>IP Resolution</td><td>{fmt(data.get('ip_resolution', {}))}</td></tr>",
        f"<tr><td>WHOIS</td><td>{fmt(data.get('whois', {}))}</td></tr>",
        f"<tr><td>DNS</td><td>{fmt(data.get('dns', {}))}</td></tr>",
        f"<tr><td>Subdomains</td><td>{fmt(subdomains)}</td></tr>",
        f"<tr><td>Open Ports</td><td>{fmt(ports)}</td></tr>",
        f"<tr><td>Service Banners</td><td>{fmt(banners)}</td></tr>",
        f"<tr><td>Detected Technologies</td><td>{fmt(technologies)}</td></tr>",
        "</table>",
        "</body></html>",
    ]
    return "\n".join(html) + "\n"


def generate_report_file(results: Dict[str, Any], output_path: Union[str, Path], output_format: str = "txt") -> str:
    """Write a report to disk and return the generated content."""
    output_path = Path(output_path)
    if output_format.lower() == "html":
        content = generate_html_report(results)
    else:
        content = generate_report(results)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return content


def build_sample_results(target: str, timestamp: str | None = None) -> Dict[str, Any]:
    """Build a minimal report payload for a target when no live results set is available."""
    if timestamp is None:
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S %Z")
    return {
        "target": target,
        "timestamp": timestamp,
        "ip_resolution": {"ipv4": ["N/A"], "ipv6": ["N/A"]},
        "whois": {"status": "not_run"},
        "dns": {"records": {"A": ["N/A"], "MX": ["N/A"], "TXT": ["N/A"], "NS": ["N/A"]}},
        "subdomains": [],
        "ports": [],
        "banners": {},
        "technologies": [],
    }


def _prompt_for_value(prompt_text: str) -> str:
    """Prompt the user for required input when running interactively."""
    value = input(prompt_text).strip()
    if not value:
        raise ValueError("Input cannot be empty.")
    return value


def main(argv=None) -> int:
    """CLI entry point for generating a report from a target and optional output file."""
    parser = argparse.ArgumentParser(description="Generate a plain-text or HTML reconnaissance report from structured results.")
    parser.add_argument("target", nargs="?", help="Target domain or hostname to include in the report")
    parser.add_argument("--target", dest="flag_target", help="Target domain or hostname to include in the report")
    parser.add_argument("--report", help="Destination file for the generated report")
    parser.add_argument("--format", choices=["txt", "html"], default="txt", help="Output format")
    args = parser.parse_args(argv)

    target = args.flag_target or args.target
    if not target:
        try:
            target = _prompt_for_value("Enter target: ")
        except EOFError:
            print("No target provided. Exiting.")
            return 1
        except ValueError as exc:
            print(f"Error: {exc}")
            return 1

    results = build_sample_results(target)
    output = args.report or "report.txt"

    try:
        content = generate_report_file(results, output, output_format=args.format)
    except OSError as exc:
        print(f"Error writing report: {exc}")
        return 1

    print(content)
    print(f"Report written to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
