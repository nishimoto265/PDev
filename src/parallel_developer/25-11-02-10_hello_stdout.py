"""Simple script that prints HELLO with detailed file logging."""

from __future__ import annotations

import logging
import sys
from pathlib import Path


LOG_FILENAME = "25-11-02-10_hello_stdout.log"
LOGGER_NAME = "parallel_developer.hello_stdout.25_11_02_10"


def _configure_logger() -> logging.Logger:
    """Create a dedicated file logger for the HELLO stdout script."""

    project_root = Path(__file__).resolve().parents[2]
    logs_dir = project_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler(logs_dir / LOG_FILENAME, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


def main() -> int:
    logger = _configure_logger()
    logger.debug("hello_stdout_script_start")

    message = "HELLO"
    logger.debug("hello_stdout_script_message_prepared message=%s", message)
    print(message)

    logger.debug("hello_stdout_script_complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
