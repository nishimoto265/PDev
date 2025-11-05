import asyncio
from pathlib import Path
from unittest.mock import Mock

import pytest

from parallel_developer.controller import CLIController
from parallel_developer.orchestrator import OrchestrationResult
from parallel_developer.session_manifest import ManifestStore


def _run(coro):
    return asyncio.run(coro)


class DummyOrchestrator:
    def __init__(self, controller, result, during_run=None):
        self._controller = controller
        self._result = result
        self._during_run = during_run
        self._tmux = Mock()

    def run_cycle(self, instruction, selector, resume_session_id=None):
        if self._during_run:
            self._during_run()
        return self._result

    def set_main_session_hook(self, hook):
        self._main_hook = hook

    def set_worker_decider(self, decider):
        self._worker_decider = decider


@pytest.fixture
def base_controller(tmp_path):
    events = []

    def handler(event_type, payload):
        events.append((event_type, payload))

    controller = CLIController(
        event_handler=handler,
        orchestrator_builder=lambda **_: Mock(),
        manifest_store=ManifestStore(tmp_path / "manifests"),
        worktree_root=tmp_path,
    )
    controller._emit = lambda event, payload: events.append((event, payload))
    async def _noop_handle_attach(**kwargs):
        return None

    controller._handle_attach_command = _noop_handle_attach  # type: ignore[attr-defined]
    controller._attach_mode = "manual"
    return controller, events


def test_workflow_continue_requests(base_controller, monkeypatch):
    controller, events = base_controller

    result = OrchestrationResult(
        selected_session="session-123",
        sessions_summary={"worker": {"score": 90}},
        continue_requested=True,
    )

    orchestrator = DummyOrchestrator(controller, result)
    controller._builder = lambda **kwargs: orchestrator

    _run(controller._workflow.run_instruction("Implement feature"))

    assert controller._last_selected_session == "session-123"
    assert controller._last_scoreboard == {}
    assert any("継続" in payload.get("text", "") for event, payload in events if event == "log")


def test_workflow_cancel_replays_queued(base_controller):
    controller, _ = base_controller

    def during_run():
        controller._cancelled_cycles.add(controller._cycle_counter)

    result_cancel = OrchestrationResult(selected_session="session-a", sessions_summary={})
    result_followup = OrchestrationResult(selected_session="session-b", sessions_summary={"main": {"selected": True}})

    orchestrators = [
        DummyOrchestrator(controller, result_cancel, during_run=during_run),
        DummyOrchestrator(controller, result_followup),
    ]

    def builder(**kwargs):
        return orchestrators.pop(0)

    controller._builder = builder
    controller._queued_instruction = "second pass"

    _run(controller._workflow.run_instruction("first pass"))

    assert controller._queued_instruction is None
    assert controller._last_selected_session == "session-b"


def test_cancelled_cycle_resumes_previous_session(base_controller):
    controller, _ = base_controller

    resume_ids = []

    class RecordingOrchestrator:
        def __init__(self, controller, session_id, cancel):
            self._controller = controller
            self._session_id = session_id
            self._cancel = cancel
            self._main_hook = None
            self._worker_decider = None
            self._tmux = Mock()

        def set_main_session_hook(self, hook):
            self._main_hook = hook

        def set_worker_decider(self, decider):
            self._worker_decider = decider

        def run_cycle(self, instruction, selector, resume_session_id=None):
            resume_ids.append(resume_session_id)
            if self._main_hook:
                self._main_hook(self._session_id)
            if self._cancel:
                self._controller._cancelled_cycles.add(self._controller._cycle_counter)
            return OrchestrationResult(
                selected_session=self._session_id,
                sessions_summary={},
            )

    controller._cycle_history = [
        {
            "cycle_id": 1,
            "selected_session": "session-prev",
            "scoreboard": {},
            "instruction": "previous",
        }
    ]
    controller._last_selected_session = "session-prev"
    controller._active_main_session_id = "session-prev"

    orchestrators = [
        RecordingOrchestrator(controller, "session-new", cancel=True),
        RecordingOrchestrator(controller, "session-next", cancel=False),
    ]

    def builder(**kwargs):
        return orchestrators.pop(0)

    controller._builder = builder

    _run(controller._workflow.run_instruction("first cancelled"))
    assert resume_ids[0] == "session-prev"
    assert controller._last_selected_session == "session-prev"

    _run(controller._workflow.run_instruction("second run"))
    assert resume_ids[1] == "session-prev"


def test_first_cycle_cancel_keeps_current_session(base_controller):
    controller, _ = base_controller

    resume_ids = []

    class RecordingOrchestrator:
        def __init__(self, controller, session_id):
            self._controller = controller
            self._session_id = session_id
            self._main_hook = None
            self._worker_decider = None
            self._tmux = Mock()

        def set_main_session_hook(self, hook):
            self._main_hook = hook

        def set_worker_decider(self, decider):
            self._worker_decider = decider

        def run_cycle(self, instruction, selector, resume_session_id=None):
            resume_ids.append(resume_session_id)
            if self._main_hook:
                self._main_hook(self._session_id)
            self._controller._cancelled_cycles.add(self._controller._cycle_counter)
            return OrchestrationResult(
                selected_session=self._session_id,
                sessions_summary={},
            )

    orchestrators = [RecordingOrchestrator(controller, "session-new"), RecordingOrchestrator(controller, "session-next")]

    def builder(**kwargs):
        return orchestrators.pop(0)

    controller._builder = builder

    _run(controller._workflow.run_instruction("first cancelled"))
    assert resume_ids[0] is None
    assert controller._last_selected_session is None

    _run(controller._workflow.run_instruction("second run"))
    assert resume_ids[1] is None
