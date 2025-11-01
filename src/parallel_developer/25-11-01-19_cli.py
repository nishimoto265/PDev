"""Typer CLI entrypoint for the parallel developer orchestrator."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import typer

from .orchestrator import Orchestrator
from .services import (
    BossManager,
    CodexMonitor,
    LogManager,
    TmuxLayoutManager,
    WorktreeManager,
)

app = typer.Typer(add_completion=False, no_args_is_help=True, invoke_without_command=True)


@app.callback()
def main(
    instruction: Annotated[
        str,
        typer.Option(
            "--instruction",
            "-i",
            prompt="指示を入力してください",
            help="Codexへ送信する指示文",
        ),
    ],
    workers: Annotated[
        int, typer.Option("--workers", "-w", min=1, help="並列workerの数")
    ] = 3,
    log_dir: Annotated[
        Optional[Path],
        typer.Option("--log-dir", help="ログ出力先ディレクトリ（未指定の場合は自動生成）"),
    ] = None,
) -> None:
    """Execute a full orchestrated cycle for the given instruction."""

    orchestrator = build_orchestrator(worker_count=workers, log_dir=log_dir)
    result = orchestrator.run_cycle(instruction)

    typer.echo("\n=== Scoreboard (auto-evaluated) ===")
    for key, data in sorted(
        result.sessions_summary.items(),
        key=lambda item: item[1].get("score", 0.0),
        reverse=True,
    ):
        score = data.get("score", 0.0)
        comment = data.get("comment", "")
        typer.echo(f"{key:>10}: {score:.2f}" + (f"  # {comment}" if comment else ""))

    typer.echo(f"\n[parallel-dev] Selected session: {result.selected_session}")


def build_orchestrator(worker_count: int, log_dir: Optional[Path]) -> Orchestrator:
    """Factory for an Orchestrator instance."""

    session_name = "parallel-dev"
    timestamp = datetime.utcnow().strftime("%y-%m-%d-%H%M%S")

    base_logs_dir = Path(log_dir) if log_dir else Path("logs") / timestamp
    base_logs_dir.mkdir(parents=True, exist_ok=True)
    session_map_path = base_logs_dir / "sessions_map.yaml"

    monitor = CodexMonitor(
        logs_dir=base_logs_dir,
        session_map_path=session_map_path,
    )
    worktree_root = Path.cwd()
    tmux_manager = TmuxLayoutManager(
        session_name=session_name,
        worker_count=worker_count,
        monitor=monitor,
        root_path=worktree_root,
    )
    worktree_manager = WorktreeManager(root=worktree_root, worker_count=worker_count)
    boss_manager = BossManager(repo_path=worktree_root)
    log_manager = LogManager(logs_dir=base_logs_dir)

    return Orchestrator(
        tmux_manager=tmux_manager,
        worktree_manager=worktree_manager,
        monitor=monitor,
        boss_manager=boss_manager,
        log_manager=log_manager,
        worker_count=worker_count,
        session_name=session_name,
    )
