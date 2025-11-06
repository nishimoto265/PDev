"""Compatibility wrapper for the evening script."""
from __future__ import annotations

import importlib.util
from pathlib import Path

def _load_impl():
    module_path = Path(__file__).with_name("25-11-06-15_evening.py")
    spec = importlib.util.spec_from_file_location("dev_test.evening_impl", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load evening implementation from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = _load_impl()
    module.main()


if __name__ == "__main__":
    main()
