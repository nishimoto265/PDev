from pathlib import Path
from unittest.mock import Mock

import pytest

from parallel_developer import cli


@pytest.fixture(autouse=True)
def isolate_env(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    yield


def test_build_orchestrator_wires_dependencies(monkeypatch):
    tmux = Mock(name="TmuxManager")
    worktree = Mock(name="WorktreeManager")
    monitor = Mock(name="CodexMonitor")
    log_manager = Mock(name="LogManager")
    orchestrator_instance = Mock(name="OrchestratorInstance")

    def fake_tmux(**kwargs):
        assert kwargs["session_namespace"] == "namespace"
        assert kwargs["codex_home"] == Path("codex-home")
        return tmux

    monkeypatch.setattr(
        "parallel_developer.cli.TmuxLayoutManager",
        fake_tmux,
    )

    def fake_worktree(**kwargs):
        assert kwargs["session_namespace"] == "namespace"
        return worktree

    monkeypatch.setattr(
        "parallel_developer.cli.WorktreeManager", fake_worktree
    )

    def fake_monitor(**kwargs):
        assert kwargs["codex_sessions_root"] == Path("codex-home/.codex/sessions")
        return monitor

    monkeypatch.setattr(
        "parallel_developer.cli.CodexMonitor",
        fake_monitor,
    )
    monkeypatch.setattr("parallel_developer.cli.LogManager", lambda **_: log_manager)
    monkeypatch.setattr(
        "parallel_developer.cli.Orchestrator",
        lambda **kwargs: orchestrator_instance,
    )

    result = cli.build_orchestrator(worker_count=3, log_dir=None, session_namespace="namespace", codex_home=Path("codex-home"))

    assert result is orchestrator_instance
    tmux.ensure_layout.assert_not_called()
