#!/usr/bin/env python3
"""Detailed Good evening again script with verbose file logging."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Sequence

DEFAULT_RECIPIENT = "world"
MESSAGE_TEMPLATE = "Good evening again, {recipient}!"
LOGGER_NAME = "dev_test.25-11-10-13_evening2"
LOG_FILENAME = "25-11-10-13_evening2.log"


def _log_path() -> Path:
    """Return the repository-relative log file path and ensure directories exist."""

    repo_root = Path(__file__).resolve().parents[1]
    logs_dir = repo_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    return logs_dir / LOG_FILENAME


def _configure_logger() -> logging.Logger:
    """Configure a file logger that captures every step of the script."""

    log_path = _log_path()
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)

    has_handler = any(
        isinstance(handler, logging.FileHandler)
        and Path(getattr(handler, "baseFilename", "")) == log_path
        for handler in logger.handlers
    )
    if not has_handler:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
            )
        )
        logger.addHandler(handler)

    logger.propagate = False
    return logger


def run(
    recipient: str = DEFAULT_RECIPIENT,
    *,
    logger: logging.Logger | None = None,
) -> str:
    """Prepare the greeting message while writing detailed logs."""

    active_logger = logger or _configure_logger()
    active_logger.debug("evening2_run_start recipient=%s", recipient)
    message = MESSAGE_TEMPLATE.format(recipient=recipient)
    active_logger.info(
        "evening2_message_prepared recipient=%s message=%s", recipient, message
    )
    active_logger.debug("evening2_run_complete recipient=%s", recipient)
    return message


def main(argv: Sequence[str] | None = None) -> str:
    """Entry point for CLI execution."""

    parser = argparse.ArgumentParser(
        description="Emit a Good evening again greeting with verbose file logging."
    )
    parser.add_argument(
        "--recipient",
        default=DEFAULT_RECIPIENT,
        help="Name to greet. Defaults to '%(default)s'.",
    )
    args = parser.parse_args(argv)

    logger = _configure_logger()
    logger.debug("evening2_cli_start argv=%s", argv if argv is not None else [])
    message = run(args.recipient, logger=logger)
    print(message)
    logger.info("evening2_message_emitted recipient=%s", args.recipient)
    logger.debug("evening2_cli_complete recipient=%s", args.recipient)
    return message


if __name__ == "__main__":
    main()
