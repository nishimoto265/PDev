from unittest.mock import Mock

from typer.testing import CliRunner

from parallel_developer.cli import app


def test_cli_prompt_invokes_orchestrator(monkeypatch):
    runner = CliRunner()

    orchestrator_mock = Mock(name="orchestrator")
    monkeypatch.setattr(
        "parallel_developer.cli.build_orchestrator",
        lambda worker_count, log_dir: orchestrator_mock,
    )

    result = runner.invoke(
        app,
        ["--workers", "4", "--instruction", "Ship-it"],
    )

    assert result.exit_code == 0
    orchestrator_mock.run_cycle.assert_called_once_with("Ship-it")
