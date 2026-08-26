# 2nd_recon_tool

This repository is currently implementing the third planned feature branch: `feature/port-scanner`.

## Current functionality

The project now includes a lightweight TCP port scanner for a user-supplied hostname or IP address. It validates the target, scans common ports by default, and reports which ones are open while handling refusal and timeout conditions gracefully.

Included behaviors:

- Target validation for domains and IP addresses
- Default scanning of common reconnaissance ports
- Optional custom port or port-range input
- Timeout handling for slow or filtered services
- Structured results for open and closed ports
- Graceful error messaging for invalid targets and DNS failures

## Project structure

```text
recon-tool/
├── README.md
├── requirements.txt
├── plan.md
├── recon/
│   ├── __init__.py
│   ├── port_scanner.py
│   └── subdomains.py
└── tests/
    ├── test_port_scanner.py
    └── test_subdomains.py
```

## Installation

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Example usage

### Run directly from the terminal

```powershell
cd C:\Users\hassan\Documents\GitHub\2nd_recon_tool
python .\recon\port_scanner.py --target google.com --ports 80 443
```

Or use the interactive prompt:

```powershell
python .\recon\port_scanner.py
```

### Use the module in Python

```python
from recon.port_scanner import scan_ports

result = scan_ports("google.com", ports=[80, 443], timeout=1.0)
print(result)
```

## Notes

- The target must be supplied by the user.
- No domain is hard-coded in the module.
- This branch intentionally covers only the port scanning portion of the final project.
