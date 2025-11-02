import subprocess
import sys
from pathlib import Path


def test_hello_script_prints_expected_output():
    script_path = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "parallel_developer"
        / "hello_basic.py"
    )
    result = subprocess.run(
        [sys.executable, str(script_path)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, f"Script failed: {result.stderr}"
    assert result.stdout == "HELLO\n"
