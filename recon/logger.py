"""Logging configuration for the reconnaissance CLI."""

from __future__ import annotations

import logging
from typing import Optional


def configure_logger(level: str = "INFO") -> logging.Logger:
    """Create and configure the project logger."""
    normalized = str(level).upper()
    mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    log_level = mapping.get(normalized, logging.INFO)
    logger = logging.getLogger("recon_tool")
    logger.setLevel(log_level)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(log_level)
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    else:
        for handler in logger.handlers:
            handler.setLevel(log_level)

    return logger


def get_logger(level: Optional[str] = None) -> logging.Logger:
    """Return the configured logger used across the application."""
    if level is not None:
        return configure_logger(level)
    return logging.getLogger("recon_tool")
