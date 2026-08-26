# 2nd_recon_tool

This repository is currently implementing the fifth planned feature branch: `feature/reporting`.

## Current functionality

The project now includes a reporting module that turns the structured output from earlier reconnaissance modules into a readable report. It can generate plain-text and HTML summaries for the target, IP resolution, WHOIS data, DNS results, discovered subdomains, open ports, service banners, and detected technologies.

Included behaviors:

- Structured result normalization
- Plain-text reconnaissance report generation
- Optional HTML report generation
- Writing reports to disk for later review
- Clear presentation of the target and module outputs

## Project structure

```text
recon-tool/
├── README.md
├── requirements.txt
├── plan.md
├── recon/
│   ├── __init__.py
│   └── reporting.py
└── tests/
    └── test_reporting.py
```

## Example usage

```python
from recon.reporting import generate_report, generate_report_file

results = {
    "target": "google.com",
    "timestamp": "2026-08-26 12:00:00 UTC",
    "ip_resolution": {"ipv4": ["172.217.3.110"]},
    "whois": {"status": "ok"},
    "dns": {"records": {"A": ["172.217.3.110"]}},
    "subdomains": ["mail.google.com"],
    "ports": [80, 443],
    "banners": {"80": "HTTP/1.1 200 OK"},
    "technologies": ["nginx"],
}

print(generate_report(results))
generate_report_file(results, "reports/google_report.txt")
```

## Notes

- The target is supplied by the calling module or user context.
- No target is hard-coded in the module.
- This branch intentionally covers only the reporting portion of the final project.
