from unittest.mock import Mock

import pytest

from parallel_developer.services import TmuxLayoutManager


class DummyPane:
    def __init__(self, pane_id):
        self.pane_id = pane_id
        self.sent = []
        self.cmd_calls = []

    def send_keys(self, cmd, enter=True):
        self.sent.append((cmd, enter))

    def cmd(self, *args):
        self.cmd_calls.append(args)


class DummyWindow:
    def __init__(self):
        self.panes = [DummyPane("%0")]
        self.select_layout_args = []

    def split_window(self, attach=False):
        pane = DummyPane(f"%{len(self.panes)}")
        self.panes.append(pane)
        return pane

    def select_layout(self, layout):
        self.select_layout_args.append(layout)


class DummySession:
    def __init__(self, name):
        self.session_name = name
        self.windows = [DummyWindow()]
        self.attached_window = self.windows[0]


class DummyServer:
    def __init__(self):
        self.sessions = []
        self.new_session_args = []

    def find_where(self, attrs):
        for session in self.sessions:
            if session.session_name == attrs.get("session_name"):
                return session
        return None

    def new_session(self, session_name, attach):
        session = DummySession(session_name)
        self.sessions.append(session)
        self.new_session_args.append((session_name, attach))
        return session


@pytest.fixture
def monkeypatch_server(monkeypatch):
    server = DummyServer()
    monkeypatch.setattr("parallel_developer.services.libtmux.Server", lambda: server)
    return server


def test_tmux_layout_manager_allocates_panes(monkeypatch_server):
    monitor = Mock()
    monitor.await_new_sessions.return_value = {
        "%2": "session-worker-1",
        "%3": "session-worker-2",
    }

    manager = TmuxLayoutManager(session_name="parallel-dev", worker_count=2, monitor=monitor)

    layout = manager.ensure_layout(session_name="parallel-dev", worker_count=2)
    assert layout["main"] == "%0"
    assert layout["boss"] == "%1"
    assert layout["workers"] == ["%2", "%3"]

    manager.send_instruction_to_pane(pane_id=layout["main"], instruction="echo main")
    manager.send_instruction_to_workers(
        fork_map={layout["workers"][0]: "session-worker-1"},
        instruction="echo worker",
    )

    fork_map = manager.fork_workers(workers=layout["workers"], base_session_id="session-main")
    assert fork_map == {
        layout["workers"][0]: "session-worker-1",
        layout["workers"][1]: "session-worker-2",
    }
    monitor.await_new_sessions.assert_called_once()

    manager.promote_to_main(session_id="session-worker-1", pane_id=layout["main"])

    main_pane = monkeypatch_server.sessions[0].windows[0].panes[0]
    assert main_pane.sent[0] == ("echo main", True)
    worker_pane = monkeypatch_server.sessions[0].windows[0].panes[2]
    assert ("send-keys", "-t", layout["workers"][0], "Escape") in worker_pane.cmd_calls
    assert worker_pane.sent[0] == ("echo worker", True)
    assert main_pane.sent[-1] == ("codex resume session-worker-1", True)
