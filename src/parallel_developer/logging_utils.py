"""Utility helpers for logging within example scripts."""

from __future__ import annotations

import logging
from pathlib import Path


def configure_file_logger(logger_name: str, log_filename: str) -> logging.Logger:
    """Create or reuse a DEBUG logger that writes to ``logs/log_filename``."""

    logs_dir = Path(__file__).resolve().parents[2] / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    log_path = logs_dir / log_filename
    if not _has_handler(logger, log_path):
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def _has_handler(logger: logging.Logger, log_path: Path) -> bool:
    target = str(log_path.resolve())
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            handler_path = Path(getattr(handler, "baseFilename", "")).resolve()
            if handler_path == log_path or str(handler_path) == target:
                return True
    return False
