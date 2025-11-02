from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_script_prints_hello() -> None:
    script_path = Path(__file__).resolve().parents[1] / "src" / "25-11-02-10_hello.py"

    result = subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "HELLO\n"
