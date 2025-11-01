from pathlib import Path

import git

from parallel_developer.orchestrator import CandidateInfo, SelectionDecision
from parallel_developer.services import BossManager


def test_boss_manager_prefers_highest_score(tmp_path: Path):
    repo = git.Repo.init(tmp_path, initial_branch="main")
    base = tmp_path / "README.md"
    base.write_text("base\n", encoding="utf-8")
    repo.index.add([str(base)])
    repo.index.commit("init")

    manager = BossManager(repo_path=tmp_path)
    completion = {
        "session-a": {"done": True, "score": 75},
        "session-b": {"done": True, "score": 90},
        "session-c": {"done": True, "score": 40},
    }

    candidates = [
        CandidateInfo(
            key="worker-1",
            label="worker-1 (session session-a)",
            session_id="session-a",
            branch="parallel-dev/worker-1",
            worktree=Path("/tmp/worker-1"),
        ),
        CandidateInfo(
            key="worker-2",
            label="worker-2 (session session-b)",
            session_id="session-b",
            branch="parallel-dev/worker-2",
            worktree=Path("/tmp/worker-2"),
        ),
        CandidateInfo(
            key="boss",
            label="boss (session session-boss)",
            session_id="session-boss",
            branch="parallel-dev/boss",
            worktree=Path("/tmp/boss"),
        ),
    ]

    decision = SelectionDecision(
        selected_key="worker-2",
        scores={"worker-1": 75, "worker-2": 90, "boss": 85},
        comments={"worker-2": "best"},
    )

    scoreboard = manager.finalize_scores(candidates, decision, completion)

    assert scoreboard["worker-2"]["score"] == 90
    assert scoreboard["worker-2"]["comment"] == "best"
    assert scoreboard["worker-2"]["done"] is True
    assert scoreboard["boss"]["done"] is True


def test_boss_manager_auto_select(tmp_path: Path):
    repo = git.Repo.init(tmp_path, initial_branch="main")
    base = tmp_path / "README.md"
    base.write_text("base\n", encoding="utf-8")
    repo.index.add([str(base)])
    repo.index.commit("init")

    worker_branch = "parallel-dev/worker-1"
    repo.git.branch(worker_branch)
    repo.git.checkout(worker_branch)
    feature = tmp_path / "feature.txt"
    feature.write_text("change\n", encoding="utf-8")
    repo.index.add([str(feature)])
    repo.index.commit("feat")
    repo.git.checkout("main")

    manager = BossManager(repo_path=tmp_path)
    candidate = CandidateInfo(
        key="worker-1",
        label="worker-1",
        session_id="session-worker-1",
        branch=worker_branch,
        worktree=tmp_path,
    )
    decision, summary = manager.auto_select(
        [candidate],
        completion={"session-worker-1": {"done": True}},
    )

    assert decision.selected_key == "worker-1"
    assert summary["worker-1"]["score"] > 60
