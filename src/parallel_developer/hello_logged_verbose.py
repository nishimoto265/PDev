"""Print HELLO to stdout with extra diagnostic logging."""

from __future__ import annotations

import sys
from pathlib import Path


if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from parallel_developer.logging_utils import configure_file_logger  # noqa: E402


LOGGER_NAME = "parallel_developer.hello_logged_verbose"
LOG_FILENAME = "hello_logged_verbose.log"


def main() -> int:
    logger = configure_file_logger(LOGGER_NAME, LOG_FILENAME)
    logger.debug("hello_logged_verbose_start")

    message = "HELLO"
    logger.debug("hello_logged_verbose_message_prepared message=%s", message)
    print(message)

    logger.debug("hello_logged_verbose_complete")
    return 0


if __name__ == "__main__":
    sys.exit(main())
