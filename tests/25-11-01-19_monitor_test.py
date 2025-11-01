import json
import time
from pathlib import Path

import pytest

from parallel_developer.services import CodexMonitor


def test_monitor_registers_and_logs_instruction(tmp_path: Path):
    session_map = tmp_path / "sessions_map.yaml"
    monitor = CodexMonitor(logs_dir=tmp_path, session_map_path=session_map, poll_interval=0.01)

    rollout = tmp_path / "sessions" / "rollout-main.jsonl"
    rollout.write_text("", encoding="utf-8")

    monitor.register_session(
        pane_id="pane-main",
        session_id="session-main",
        rollout_path=rollout,
    )

    session_id = monitor.capture_instruction(pane_id="pane-main", instruction="Build feature")
    assert session_id == "session-main"

    instruction_log = tmp_path / "instruction.log"
    log_entries = [json.loads(line) for line in instruction_log.read_text(encoding="utf-8").splitlines()]
    assert log_entries == [{"pane": "pane-main", "instruction": "Build feature"}]


def test_monitor_waits_for_done(tmp_path: Path):
    session_map = tmp_path / "sessions_map.yaml"
    monitor = CodexMonitor(logs_dir=tmp_path, session_map_path=session_map, poll_interval=0.01)

    rollout_a = tmp_path / "sessions" / "rollout-a.jsonl"
    rollout_b = tmp_path / "sessions" / "rollout-b.jsonl"
    rollout_a.write_text("", encoding="utf-8")
    rollout_b.write_text("", encoding="utf-8")

    monitor.register_session(pane_id="pane-a", session_id="session-a", rollout_path=rollout_a)
    monitor.register_session(pane_id="pane-b", session_id="session-b", rollout_path=rollout_b)

    completion = monitor.await_completion(session_ids=["session-a", "session-b"], timeout_seconds=0.05)
    assert completion["session-a"]["done"] is False
    assert completion["session-b"]["done"] is False

    rollout_a.write_text('{"item": "note"}\n{"content": "/done"}\n', encoding="utf-8")
    rollout_b.write_text('{"item": "task"}\n{"content": "/done"}\n', encoding="utf-8")

    completion = monitor.await_completion(session_ids=["session-a", "session-b"], timeout_seconds=0.1)
    assert completion["session-a"]["done"] is True
    assert completion["session-b"]["done"] is True


def test_monitor_detects_new_sessions(tmp_path: Path):
    session_map = tmp_path / "sessions_map.yaml"
    monitor = CodexMonitor(logs_dir=tmp_path, session_map_path=session_map, poll_interval=0.01)

    rollout_main = tmp_path / "sessions" / "rollout-main.jsonl"
    rollout_main.write_text("", encoding="utf-8")
    monitor.register_session(pane_id="pane-worker-1", session_id="session-main", rollout_path=rollout_main)

    # Simulate background process registering new session id after fork
    monitor.register_session(pane_id="pane-worker-1", session_id="session-worker", rollout_path=rollout_main)

    mapping = monitor.await_new_sessions(
        worker_panes=["pane-worker-1"],
        base_session_id="session-main",
        timeout_seconds=0.1,
    )

    assert mapping == {"pane-worker-1": "session-worker"}
