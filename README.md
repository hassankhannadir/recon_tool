# 2nd_recon_tool

This repository is currently implementing the fourth planned feature branch: `feature/banner-tech`.

## Current functionality

The project now includes banner grabbing and lightweight technology detection for a user-supplied host or URL. It opens a socket to a target port, reads the banner if one is exposed, and performs a basic HTTP fingerprint using headers and metadata.

Included behaviors:

- Banner grabbing over TCP sockets
- Timeout and refusal handling
- Domain/IP validation
- HTTP technology detection from headers and HTML metadata
- Graceful error reporting for unreachable or unsupported services

## Project structure

```text
recon-tool/
├── README.md
├── requirements.txt
├── plan.md
├── recon/
│   ├── __init__.py
│   └── banner_tech.py
└── tests/
    └── test_banner_tech.py
```

## Installation

```bash
python -m venv .venv
. .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Example usage

```python
from recon.banner_tech import detect_technologies, grab_banner

print(grab_banner("google.com", 80))
print(detect_technologies("https://google.com"))
```

You can also run the module directly:

```powershell
cd C:\Users\hassan\Documents\GitHub\2nd_recon_tool
python .\recon\banner_tech.py
```

## Notes

- The target must be supplied by the user.
- No target is hard-coded.
- This branch intentionally covers only the banner grabbing and technology detection portion of the final project.
