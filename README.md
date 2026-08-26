# 2nd_recon_tool

This repository contains a modular reconnaissance toolkit built in stages. The project includes DNS/WHOIS lookups, passive subdomain discovery, active port scanning, banner grabbing, HTTP technology detection, report generation, and a final CLI/logging layer.

## Current status

The main branch contains the integrated reconnaissance project after merging the completed feature branches.

## Included modules

- WHOIS + DNS enumeration
- Passive subdomain discovery
- Port scanning
- Banner grabbing and technology detection
- Report generation
- Final CLI and logging

## Project structure

```text
recon-tool/
├── README.md
├── main.py
├── plan.md
├── requirements.txt
├── report.txt
├── recon/
│   ├── __init__.py
│   ├── banner_tech.py
│   ├── logger.py
│   ├── port_scanner.py
│   ├── reporting.py
│   ├── subdomains.py
│   └── whois_dns.py
├── reports/
│   └── google_report.txt
└── tests/
    ├── test_banner_tech.py
    ├── test_cli_logging.py
    ├── test_port_scanner.py
    ├── test_reporting.py
    ├── test_subdomains.py
    └── test_whois_dns.py
```

## Installation

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the project

From the repository root, use the CLI:

```powershell
cd C:\Users\hassan\Documents\GitHub\2nd_recon_tool
python .\main.py --domain google.com --dns
python .\main.py --target google.com --ports 80 443
python .\main.py --target google.com --banner
```

You can also run individual modules directly:

```powershell
python .\recon\whois_dns.py
python .\recon\subdomains.py
python .\recon\port_scanner.py
python .\recon\banner_tech.py
python .\recon\reporting.py
```

## Notes

- Targets are user-supplied and not hard-coded.
- The modules are designed to work independently, and the final CLI brings them together.
- This repository is intended for demonstration and educational reconnaissance workflows.
