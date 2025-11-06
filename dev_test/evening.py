"""Entry point wrapper for the evening script with detailed diagnostics."""
from __future__ import annotations

import importlib.util
import logging
from pathlib import Path

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "25-11-06-15_evening_wrapper.log"


def configure_logger() -> logging.Logger:
    """Set up a verbose logger for tracing wrapper execution."""
    logger = logging.getLogger("dev_test.evening.wrapper")
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
    logger.debug("wrapper_logger_configured")
    return logger


def _load_impl(module_path: Path):
    """Load the timestamped implementation module from disk."""
    logger = configure_logger()
    logger.debug("module_load_start: path=%s", module_path)

    spec = importlib.util.spec_from_file_location("dev_test.evening_impl", module_path)
    if spec is None or spec.loader is None:
        logger.error("module_spec_failed: path=%s", module_path)
        raise ImportError(f"Unable to load evening implementation from {module_path}")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("module_exec_failed: path=%s", module_path)
        raise RuntimeError("Evening implementation execution failed") from exc

    logger.debug("module_load_complete: path=%s", module_path)
    return module


def main() -> None:
    """Invoke the timestamped evening script without silent fallbacks."""
    logger = configure_logger()
    module_path = Path(__file__).with_name("25-11-06-15_evening.py")
    logger.info("evening_wrapper_start: path=%s", module_path)

    module = _load_impl(module_path)
    try:
        module.main()
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.exception("evening_wrapper_failed")
        raise RuntimeError("Evening wrapper failed") from exc

    logger.info("evening_wrapper_complete")


if __name__ == "__main__":
    main()
