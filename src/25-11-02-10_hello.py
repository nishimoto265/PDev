from __future__ import annotations

import logging
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[1] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "25-11-02-10_hello.log"


def _get_logger() -> logging.Logger:
    logger = logging.getLogger("hello_script")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


def main() -> None:
    logger = _get_logger()
    logger.debug("hello_script_start")

    message = "HELLO"
    logger.debug("hello_script_message_prepared message=%s", message)

    print(message)

    logger.debug("hello_script_stdout_write_completed")
    logger.info("HELLO written to standard output.")


if __name__ == "__main__":
    main()
