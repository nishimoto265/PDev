import yaml
from pathlib import Path

from parallel_developer.services import LogManager


def test_log_manager_writes_cycle_summary(tmp_path: Path):
    manager = LogManager(logs_dir=tmp_path)

    manager.record_cycle(
        instruction="Deploy",
        layout={"main": "pane-main", "boss": "pane-boss", "workers": ["worker-1"]},
        fork_map={"worker-pane": "session-worker"},
        completion={"session-worker": {"done": True}},
        result=type("Result", (), {"selected_session": "session-worker"})(),
    )

    cycles_dir = tmp_path / "cycles"
    files = list(cycles_dir.glob("*.yaml"))
    assert len(files) == 1

    content = yaml.safe_load(files[0].read_text(encoding="utf-8"))
    assert content["instruction"] == "Deploy"
    assert content["result"]["selected_session"] == "session-worker"
