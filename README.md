# 2nd_recon_tool

This repository is currently implementing the final planned feature branch: `feature/cli-logging`.

## Current functionality

The project now includes the final CLI and logging layer for the reconnaissance application. It supports interactive domain entry, module selection, command-line flags, verbosity levels, and a structured JSON/text output model for running modules when they are available in the workspace.

Included behaviors:

- Domain and flag-based CLI parsing with argparse
- Interactive prompt for domain selection
- Multiple module execution choices
- Logging configuration with INFO/DEBUG verbosity
- Safe module loading so unavailable feature modules report a clear status instead of crashing the app

## Project structure

```text
recon-tool/
├── README.md
├── requirements.txt
├── plan.md
├── main.py
├── recon/
│   ├── __init__.py
│   └── logger.py
└── tests/
    └── test_cli_logging.py
```

## Example usage

```powershell
cd C:\Users\hassan\Documents\GitHub\2nd_recon_tool
python .\main.py --domain google.com --dns --json
python .\main.py --domain google.com --all --verbose
python .\main.py
```

## Notes

- The target domain must be provided by the user.
- This branch covers the final CLI and logging architecture only.
- Earlier modules remain independent and can be plugged into this interface when present in the workspace.
