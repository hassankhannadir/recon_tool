from __future__ import annotations

import logging

from recon.logger import configure_logger, get_logger


def test_configure_logger_sets_level():
    logger = configure_logger("DEBUG")
    assert logger.level == logging.DEBUG


def test_get_logger_returns_logger():
    logger = get_logger()
    assert isinstance(logger, logging.Logger)


def test_main_handles_flagged_domain(monkeypatch):
    import main

    monkeypatch.setattr("sys.argv", ["main.py", "--domain", "google.com", "--dns", "--json"])
    exit_code = main.main()
    assert exit_code == 0
