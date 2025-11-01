from parallel_developer.orchestrator import OrchestrationResult
from parallel_developer.services import BossManager


def test_boss_manager_prefers_highest_score():
    manager = BossManager()
    completion = {
        "session-a": {"done": True, "score": 75},
        "session-b": {"done": True, "score": 90},
        "session-c": {"done": True, "score": 40},
    }

    result = manager.select_best(
        main_session_id="session-main",
        worker_sessions={"pane-1": "session-a", "pane-2": "session-b", "pane-3": "session-c"},
        completion=completion,
    )

    assert isinstance(result, OrchestrationResult)
    assert result.selected_session == "session-b"
    assert result.sessions_summary["session-b"]["score"] == 90
