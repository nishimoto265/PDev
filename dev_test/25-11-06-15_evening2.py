"""Second evening greeting script."""
from __future__ import annotations

import logging
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "25-11-06-15_evening2.log"


def configure_logger() -> logging.Logger:
    logger = logging.getLogger("dev_test.evening2")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(LOG_PATH)
    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    logger.debug("logger_configured")
    return logger


def run() -> str:
    logger = configure_logger()
    logger.info("evening2_script_start")
    message = "Good evening again, world!"
    logger.debug("message_prepared: %s", message)
    logger.info("evening2_script_message_ready")
    logger.info("evening2_script_complete")
    return message


def main() -> None:
    logger = configure_logger()
    logger.debug("main_invoked")
    message = run()
    print(message)
    logger.debug("main_completed")


if __name__ == "__main__":
    main()
