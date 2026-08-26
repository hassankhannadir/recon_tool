"""Final CLI for the reconnaissance project."""

from __future__ import annotations

import argparse
import importlib
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

from recon.logger import configure_logger


def _safe_import(module_name: str):
    """Import a module if it exists; return None when unavailable."""
    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None


def _normalize_domain(domain: Optional[str]) -> str:
    """Validate a user-provided target domain."""
    if domain is None:
        raise ValueError("A target domain is required.")
    clean = domain.strip().lower().rstrip(".")
    if not clean:
        raise ValueError("A target domain is required.")
    return clean


def _run_module(module_name: str, function_name: str, domain: str, logger: logging.Logger) -> Dict[str, Any]:
    """Execute an optional module function and return its output as a dictionary."""
    module = _safe_import(module_name)
    if module is None:
        logger.warning("Module %s is not available in this workspace yet.", module_name)
        return {"status": "not_available", "module": module_name}

    if not hasattr(module, function_name):
        logger.warning("Function %s was not found in %s.", function_name, module_name)
        return {"status": "not_implemented", "module": module_name, "function": function_name}

    try:
        result = getattr(module, function_name)(domain)
    except TypeError:
        try:
            result = getattr(module, function_name)(domain, timeout=5)
        except TypeError:
            result = getattr(module, function_name)(domain, port=80)
    return result if isinstance(result, dict) else {"status": "ok", "result": result}


def _run_port_scan(domain: str, logger: logging.Logger) -> Dict[str, Any]:
    """Run the port-scanning function when available."""
    module = _safe_import("recon.port_scanner")
    if module is None:
        logger.warning("Port scanner module is not available in this workspace yet.")
        return {"status": "not_available", "module": "recon.port_scanner"}
    try:
        return module.scan_ports(domain, ports=[80, 443, 8080], timeout=1.0)
    except Exception as exc:  # pragma: no cover - runtime-dependent path
        logger.error("Port scan failed for %s: %s", domain, exc)
        return {"status": "error", "module": "recon.port_scanner", "error": str(exc)}


def _run_banner_grab(domain: str, logger: logging.Logger) -> Dict[str, Any]:
    """Run banner grabbing when the banner module is available."""
    module = _safe_import("recon.banner_tech")
    if module is None:
        logger.warning("Banner/technology module is not available in this workspace yet.")
        return {"status": "not_available", "module": "recon.banner_tech"}
    try:
        return module.grab_banner(domain, 80)
    except Exception as exc:  # pragma: no cover - runtime-dependent path
        logger.error("Banner grab failed for %s: %s", domain, exc)
        return {"status": "error", "module": "recon.banner_tech", "error": str(exc)}


def _run_tech_scan(domain: str, logger: logging.Logger) -> Dict[str, Any]:
    """Run technology detection when the banner module is available."""
    module = _safe_import("recon.banner_tech")
    if module is None:
        logger.warning("Technology detection module is not available in this workspace yet.")
        return {"status": "not_available", "module": "recon.banner_tech"}
    try:
        return module.detect_technologies(f"https://{domain}")
    except Exception as exc:  # pragma: no cover - runtime-dependent path
        logger.error("Technology detection failed for %s: %s", domain, exc)
        return {"status": "error", "module": "recon.banner_tech", "error": str(exc)}


def _run_all(domain: str, logger: logging.Logger) -> Dict[str, Any]:
    """Execute every available module for the given domain and aggregate it."""
    results: Dict[str, Any] = {"target": domain, "modules": {}}
    module_map = [
        ("whois", "recon.whois_dns", "whois_lookup"),
        ("dns", "recon.whois_dns", "dns_lookup"),
        ("subdomains", "recon.subdomains", "enumerate_subdomains"),
        ("ports", "recon.port_scanner", "scan_ports"),
        ("banner", "recon.banner_tech", "grab_banner"),
        ("tech", "recon.banner_tech", "detect_technologies"),
    ]

    for label, module_name, function_name in module_map:
        if module_name == "recon.port_scanner":
            results["modules"][label] = _run_port_scan(domain, logger)
        elif module_name == "recon.banner_tech" and label == "banner":
            results["modules"][label] = _run_banner_grab(domain, logger)
        elif module_name == "recon.banner_tech" and label == "tech":
            results["modules"][label] = _run_tech_scan(domain, logger)
        else:
            results["modules"][label] = _run_module(module_name, function_name, domain, logger)

    return results


def _interactive_prompt() -> str:
    """Prompt the user to enter the target domain in interactive mode."""
    print("========================================")
    print("        CUSTOM RECON TOOL")
    print("========================================")
    value = input("Enter domain: ").strip()
    if not value:
        raise ValueError("Domain cannot be empty.")
    return value


def _run_selected_modules(args: argparse.Namespace, logger: logging.Logger) -> Dict[str, Any]:
    """Execute the selected module(s) against the target domain."""
    domain = _normalize_domain(args.domain)
    results: Dict[str, Any] = {"target": domain, "modules": {}}

    if args.all:
        return _run_all(domain, logger)

    requested = []
    if args.whois:
        requested.append(("whois", "recon.whois_dns", "whois_lookup"))
    if args.dns:
        requested.append(("dns", "recon.whois_dns", "dns_lookup"))
    if args.subdomains:
        requested.append(("subdomains", "recon.subdomains", "enumerate_subdomains"))
    if args.ports:
        requested.append(("ports", "recon.port_scanner", "scan_ports"))
    if args.banner:
        requested.append(("banner", "recon.banner_tech", "grab_banner"))
    if args.tech:
        requested.append(("tech", "recon.banner_tech", "detect_technologies"))

    if not requested:
        logger.info("No module selected; running an interactive module menu.")
        print("[1] WHOIS")
        print("[2] DNS")
        print("[3] Subdomains")
        print("[4] Port Scan")
        print("[5] Banner Grab")
        print("[6] Technology Detection")
        print("[7] Run All")
        print("[0] Exit")
        choice = input("Enter choice: ").strip()
        if choice == "0":
            return {"target": domain, "modules": {"exit": {"status": "cancelled"}}}
        mapping = {
            "1": ("whois", "recon.whois_dns", "whois_lookup"),
            "2": ("dns", "recon.whois_dns", "dns_lookup"),
            "3": ("subdomains", "recon.subdomains", "enumerate_subdomains"),
            "4": ("ports", "recon.port_scanner", "scan_ports"),
            "5": ("banner", "recon.banner_tech", "grab_banner"),
            "6": ("tech", "recon.banner_tech", "detect_technologies"),
            "7": ("all", None, None),
        }
        requested = [mapping.get(choice, ("unknown", None, None))]

    for label, module_name, function_name in requested:
        if label == "all":
            results["modules"] = _run_all(domain, logger)["modules"]
            continue

        if module_name == "recon.port_scanner":
            results["modules"][label] = _run_port_scan(domain, logger)
        elif module_name == "recon.banner_tech" and label == "banner":
            results["modules"][label] = _run_banner_grab(domain, logger)
        elif module_name == "recon.banner_tech" and label == "tech":
            results["modules"][label] = _run_tech_scan(domain, logger)
        else:
            results["modules"][label] = _run_module(module_name, function_name, domain, logger)

    return results


def _print_module_result(name: str, payload: Dict[str, Any]) -> None:
    """Print a human-readable summary for a module result."""
    print(f"\n=== {name.upper()} ===")
    if not isinstance(payload, dict):
        print(payload)
        return

    status = payload.get("status", "unknown")
    print(f"Status: {status}")

    if payload.get("error"):
        print(f"Error: {payload['error']}")
        return

    if name == "whois":
        print(f"Target: {payload.get('target', 'N/A')}")
        if payload.get("server"):
            print(f"WHOIS server: {payload['server']}")
        whois_text = payload.get("whois", "")
        print(whois_text[:2000] + ("..." if len(whois_text) > 2000 else ""))
        return

    if name == "dns":
        print(f"Target: {payload.get('target', 'N/A')}")
        records = payload.get("records", {})
        for record_type in ("A", "MX", "TXT", "NS"):
            values = records.get(record_type, [])
            if values:
                print(f"{record_type}: {', '.join(values)}")
        return

    if name == "subdomains":
        print(f"Target: {payload.get('target', 'N/A')}")
        subdomains = payload.get("subdomains", [])
        if subdomains:
            print(f"Discovered subdomains ({len(subdomains)}):")
            for item in subdomains:
                print(f"  - {item}")
        else:
            print("No subdomains were discovered.")
        errors = payload.get("errors", [])
        if errors:
            print("Warnings:")
            for item in errors:
                print(f"  - {item}")
        return

    if name == "ports":
        print(f"Target: {payload.get('target', 'N/A')}")
        print(f"Scanned ports: {payload.get('scanned_ports', [])}")
        print(f"Open ports: {payload.get('open_ports', [])}")
        print(f"Closed ports: {payload.get('closed_ports', [])}")
        return

    if name == "banner":
        print(f"Host: {payload.get('host', 'N/A')}")
        print(f"Port: {payload.get('port', 'N/A')}")
        banner = payload.get("banner", "")
        if banner:
            print(f"Banner: {banner}")
        else:
            print("Banner: <no banner returned>")
        return

    if name == "tech":
        print(f"URL: {payload.get('url', 'N/A')}")
        technologies = payload.get("technologies", [])
        if technologies:
            print("Detected technologies: " + ", ".join(technologies))
        else:
            print("Detected technologies: none")
        return

    for key, value in payload.items():
        if key == "status":
            continue
        print(f"{key}: {value}")


def configure_parser() -> argparse.ArgumentParser:
    """Construct the command-line parser for the final application."""
    parser = argparse.ArgumentParser(description="Reconnaissance CLI")
    parser.add_argument("--domain", help="Target domain to examine")
    parser.add_argument("--whois", action="store_true", help="Run WHOIS lookup")
    parser.add_argument("--dns", action="store_true", help="Run DNS lookup")
    parser.add_argument("--subdomains", action="store_true", help="Run subdomain enumeration")
    parser.add_argument("--ports", action="store_true", help="Run TCP port scan")
    parser.add_argument("--banner", action="store_true", help="Grab banner from a target service")
    parser.add_argument("--tech", action="store_true", help="Detect web technologies")
    parser.add_argument("--all", action="store_true", help="Run all available modules")
    parser.add_argument("--report", help="Write the report to a text file")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--json", action="store_true", help="Print JSON output")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """CLI entry point for the completed reconnaissance application."""
    parser = configure_parser()
    args = parser.parse_args(argv)

    log_level = "DEBUG" if args.debug else "INFO"
    if args.verbose:
        log_level = "DEBUG"
    logger = configure_logger(log_level)

    try:
        if not args.domain:
            args.domain = _interactive_prompt()
        results = _run_selected_modules(args, logger)
    except ValueError as exc:
        logger.error(str(exc))
        print(f"Error: {exc}")
        return 1
    except KeyboardInterrupt:
        print("\nCancelled by user.")
        return 130

    if args.json:
        print(json.dumps(results, indent=2, sort_keys=True))
    else:
        print(f"Target: {results.get('target', 'N/A')}")
        for name, payload in results.get("modules", {}).items():
            _print_module_result(name, payload)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"Report saved to {report_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
