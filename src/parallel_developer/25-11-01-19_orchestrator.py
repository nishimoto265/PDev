"""High-level orchestration logic for parallel Codex sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, MutableMapping, Sequence


@dataclass(slots=True)
class OrchestrationResult:
    """Return value for a full orchestration cycle."""

    selected_session: str
    sessions_summary: Mapping[str, Any] = field(default_factory=dict)


class Orchestrator:
    """Coordinates tmux, git worktrees, Codex monitoring, and Boss evaluation."""

    def __init__(
        self,
        *,
        tmux_manager: Any,
        worktree_manager: Any,
        monitor: Any,
        boss_manager: Any,
        log_manager: Any,
        worker_count: int,
        session_name: str,
    ) -> None:
        self._tmux = tmux_manager
        self._worktree = worktree_manager
        self._monitor = monitor
        self._boss = boss_manager
        self._log = log_manager
        self._worker_count = worker_count
        self._session_name = session_name

    def run_cycle(self, instruction: str) -> OrchestrationResult:
        """Execute a single orchestrated instruction cycle."""

        worker_roots = list(self._worktree.prepare().values())

        layout = self._ensure_layout()
        main_pane = layout["main"]
        boss_pane = layout["boss"]
        worker_panes = layout["workers"]

        pane_to_worker_path = {}
        for idx, pane_id in enumerate(worker_panes):
            path = worker_roots[idx] if idx < len(worker_roots) else self._worktree.root
            pane_to_worker_path[pane_id] = path

        self._tmux.launch_main_session(pane_id=main_pane)
        self._tmux.launch_boss_session(pane_id=boss_pane)

        self._tmux.send_instruction_to_pane(
            pane_id=main_pane,
            instruction=instruction,
        )
        self._tmux.interrupt_pane(pane_id=main_pane)

        main_session_id = self._monitor.capture_instruction(
            pane_id=main_pane,
            instruction=instruction,
        )

        fork_map = self._tmux.fork_workers(
            workers=worker_panes,
            base_session_id=main_session_id,
        )

        self._tmux.resume_workers(fork_map, pane_to_worker_path)
        self._tmux.send_instruction_to_workers(fork_map, instruction)

        completion_info = self._monitor.await_completion(
            session_ids=list(fork_map.values())
        )

        result = self._boss.select_best(
            main_session_id=main_session_id,
            worker_sessions=fork_map,
            completion=completion_info,
        )

        if not isinstance(result, OrchestrationResult):
            raise TypeError(
                "boss_manager.select_best must return OrchestrationResult, "
                f"got {type(result)!r}"
            )

        self._tmux.promote_to_main(session_id=result.selected_session, pane_id=main_pane)

        self._log.record_cycle(
            instruction=instruction,
            layout=layout,
            fork_map=fork_map,
            completion=completion_info,
            result=result,
        )

        return result

    def _ensure_layout(self) -> MutableMapping[str, Any]:
        layout = self._tmux.ensure_layout(
            session_name=self._session_name,
            worker_count=self._worker_count,
        )
        self._validate_layout(layout)
        return layout

    def _validate_layout(self, layout: Mapping[str, Any]) -> None:
        if "main" not in layout or "boss" not in layout or "workers" not in layout:
            raise ValueError(
                "tmux_manager.ensure_layout must return mapping with "
                "'main', 'boss', and 'workers' keys"
            )
        workers = layout["workers"]
        if not isinstance(workers, Sequence):
            raise ValueError("layout['workers'] must be a sequence")
        if len(workers) != self._worker_count:
            raise ValueError(
                "tmux_manager.ensure_layout returned "
                f"{len(workers)} workers but {self._worker_count} expected"
            )
