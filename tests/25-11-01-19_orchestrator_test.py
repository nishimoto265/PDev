import pytest
from unittest.mock import Mock

from parallel_developer.orchestrator import Orchestrator, OrchestrationResult


@pytest.fixture
def dependencies():
    tmux = Mock(name="tmux_manager")
    worktree = Mock(name="worktree_manager")
    monitor = Mock(name="monitor")
    boss = Mock(name="boss_manager")
    logger = Mock(name="log_manager")

    worktree.prepare.return_value = {"worker-1": "path"}

    layout = {
        "main": "pane-main",
        "boss": "pane-boss",
        "workers": ["pane-worker-1", "pane-worker-2", "pane-worker-3"],
    }
    tmux.ensure_layout.return_value = layout

    fork_map = {
        "pane-worker-1": "session-worker-1",
        "pane-worker-2": "session-worker-2",
        "pane-worker-3": "session-worker-3",
    }
    tmux.fork_workers.return_value = fork_map

    instruction = "Implement feature X"
    monitor.capture_instruction.return_value = "session-main"
    monitor.await_completion.return_value = {
        "session-worker-1": {"done": True},
        "session-worker-2": {"done": True},
        "session-worker-3": {"done": True},
    }

    boss.select_best.return_value = OrchestrationResult(
        selected_session="session-worker-2",
        sessions_summary={
            "session-main": {"score": 0},
            "session-worker-1": {"score": 60},
            "session-worker-2": {"score": 95},
            "session-worker-3": {"score": 80},
        },
    )

    return {
        "tmux": tmux,
        "worktree": worktree,
        "monitor": monitor,
        "boss": boss,
        "logger": logger,
        "instruction": instruction,
        "fork_map": fork_map,
    }


def test_orchestrator_runs_happy_path(dependencies):
    orchestrator = Orchestrator(
        tmux_manager=dependencies["tmux"],
        worktree_manager=dependencies["worktree"],
        monitor=dependencies["monitor"],
        boss_manager=dependencies["boss"],
        log_manager=dependencies["logger"],
        worker_count=3,
        session_name="parallel-dev",
    )

    result = orchestrator.run_cycle(dependencies["instruction"])

    dependencies["worktree"].prepare.assert_called_once()
    dependencies["tmux"].ensure_layout.assert_called_once_with(
        session_name="parallel-dev",
        worker_count=3,
    )
    dependencies["tmux"].send_instruction_to_pane.assert_called_once_with(
        pane_id="pane-main",
        instruction=dependencies["instruction"],
    )
    dependencies["monitor"].capture_instruction.assert_called_once_with(
        pane_id="pane-main",
        instruction=dependencies["instruction"],
    )
    dependencies["tmux"].fork_workers.assert_called_once_with(
        workers=["pane-worker-1", "pane-worker-2", "pane-worker-3"],
        base_session_id="session-main",
    )
    dependencies["tmux"].send_instruction_to_workers.assert_called_once_with(
        dependencies["fork_map"], dependencies["instruction"]
    )
    dependencies["monitor"].await_completion.assert_called_once_with(
        session_ids=list(dependencies["fork_map"].values())
    )
    dependencies["boss"].select_best.assert_called_once()
    dependencies["tmux"].promote_to_main.assert_called_once_with(
        session_id="session-worker-2",
        pane_id="pane-main",
    )
    dependencies["logger"].record_cycle.assert_called_once()
    assert result.selected_session == "session-worker-2"
