"""Banner grabbing and lightweight technology detection."""

from __future__ import annotations

import argparse
import json
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Set

_DOMAIN_PATTERN = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+[A-Za-z]{2,63}$"
)

_TECHNOLOGY_PATTERNS = [
    "nginx",
    "apache",
    "apache tomcat",
    "gunicorn",
    "django",
    "flask",
    "express",
    "node.js",
    "react",
    "wordpress",
    "joomla",
    "drupal",
    "bootstrap",
    "jquery",
    "fastapi",
    "kubernetes",
    "cloudflare",
    "iis",
    "asp.net",
    "php",
    "openssl",
]


def validate_target(target: str) -> str:
    """Normalize and validate a hostname or IP supplied by the user."""
    if not isinstance(target, str):
        raise ValueError("Target must be a string.")

    cleaned = target.strip().lower().rstrip(".")
    if not cleaned:
        raise ValueError("Target cannot be empty.")

    if cleaned.startswith(("http://", "https://")):
        cleaned = cleaned.split("//", 1)[1]

    cleaned = cleaned.split("/", 1)[0]

    if cleaned.count(":") == 1 and cleaned.rsplit(":", 1)[0].replace(".", "", 1).isdigit():
        try:
            socket.inet_aton(cleaned.rsplit(":", 1)[0])
            return cleaned
        except OSError:
            pass

    if re.fullmatch(r"\d+\.\d+\.\d+\.\d+", cleaned):
        return cleaned

    if not _DOMAIN_PATTERN.match(cleaned):
        raise ValueError(f"Invalid target: {target!r}")

    return cleaned


def grab_banner(host: str, port: int, timeout: float = 2.0) -> Dict[str, Any]:
    """Attempt to grab a banner from a host and port using a raw TCP socket."""
    try:
        normalized_host = validate_target(host)
    except ValueError as exc:
        return {"host": host, "port": port, "status": "error", "error": str(exc)}

    if not isinstance(port, int):
        try:
            port = int(port)
        except (TypeError, ValueError):
            return {"host": normalized_host, "port": port, "status": "error", "error": "Port must be an integer."}

    if not 1 <= port <= 65535:
        return {"host": normalized_host, "port": port, "status": "error", "error": "Port must be between 1 and 65535."}

    try:
        with socket.create_connection((normalized_host, port), timeout=timeout) as sock:
            sock.settimeout(timeout)
            try:
                banner = sock.recv(1024)
            except socket.timeout:
                banner = b""
            except OSError:
                banner = b""
            decoded = banner.decode("utf-8", errors="replace").strip()
            return {"host": normalized_host, "port": port, "status": "ok", "banner": decoded or ""}
    except (socket.timeout, TimeoutError, OSError) as exc:
        return {"host": normalized_host, "port": port, "status": "error", "error": str(exc)}


def _extract_html_signals(html: str) -> Set[str]:
    """Pull likely technology markers out of meaningful HTML metadata."""
    signals: Set[str] = set()

    meta_patterns = re.findall(
        r"<meta[^>]+(?:name|property)=[\"']?([^\"'\s>]+)[\"']?[^>]*content=[\"']?([^\"'>]+)[\"']?",
        html,
        flags=re.IGNORECASE,
    )
    for name, content in meta_patterns:
        low_name = name.lower()
        low_content = content.lower()
        if "generator" in low_name or "generator" in low_content:
            signals.add(f"generator:{low_content}")
            for marker in _TECHNOLOGY_PATTERNS:
                if marker in low_content:
                    signals.add(marker)
        if "powered" in low_name or "powered" in low_content:
            signals.add(f"powered:{low_content}")
            for marker in _TECHNOLOGY_PATTERNS:
                if marker in low_content:
                    signals.add(marker)

    script_sources = re.findall(r"<script[^>]+src=[\"']([^\"']+)[\"']", html, flags=re.IGNORECASE)
    for source in script_sources:
        low_source = source.lower()
        for marker in _TECHNOLOGY_PATTERNS:
            if marker in low_source:
                signals.add(marker)

    return signals


def detect_technologies(url: str, timeout: float = 5.0) -> Dict[str, Any]:
    """Perform a lightweight HTTP-based technology fingerprint."""
    try:
        normalized = validate_target(url)
    except ValueError as exc:
        return {"url": url, "status": "error", "error": str(exc)}

    if not normalized.startswith(("http://", "https://")):
        normalized = "https://" + normalized

    try:
        request = urllib.request.Request(normalized, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            headers = dict(response.headers.items())
            html = response.read(65536).decode("utf-8", errors="replace")
            technologies = _extract_html_signals(html)

            for key, value in headers.items():
                lower_key = key.lower()
                lower_value = value.lower()
                for marker in _TECHNOLOGY_PATTERNS:
                    if marker in lower_value:
                        technologies.add(marker)
                if lower_key in {"server", "x-powered-by", "x-generator", "x-aspnet-version", "x-aspnetmvc-version"}:
                    technologies.add(f"{lower_key}:{lower_value}")
                if "cloudflare" in lower_value:
                    technologies.add("cloudflare")

            if not technologies:
                technologies = {"unknown"}

            return {
                "url": normalized,
                "status": "ok",
                "headers": headers,
                "technologies": sorted(technologies),
            }
    except (urllib.error.URLError, ValueError, OSError) as exc:
        return {"url": normalized, "status": "error", "error": str(exc)}


def main(argv: List[str] | None = None) -> int:
    """CLI entry point for banner grabbing and technology detection."""
    parser = argparse.ArgumentParser(description="Banner grab and light web technology detection for a user-supplied target.")
    parser.add_argument("target", nargs="?", help="Target URL or hostname, such as google.com or https://example.com")
    parser.add_argument("--target", dest="flag_target", help="Target URL or hostname")
    parser.add_argument("--host", dest="host_target", help="Target hostname or IP")
    parser.add_argument("--port", type=int, help="TCP port to banner-grab when using --host")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args(argv)

    target = args.flag_target or args.target or args.host_target

    if not target:
        try:
            target = input("Enter target URL or host: ").strip()
        except EOFError:
            print("No target provided. Exiting.")
            return 1

    if not target:
        print("Target cannot be empty.")
        return 1

    if args.port is not None:
        result = grab_banner(target, args.port)
    elif ":" in target and target.count(":") == 1 and not target.startswith("http"):
        host, port = target.rsplit(":", 1)
        result = grab_banner(host, int(port))
    else:
        result = detect_technologies(target)

    if args.json or True:
        print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
