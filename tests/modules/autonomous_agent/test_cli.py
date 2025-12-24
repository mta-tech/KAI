from click.testing import CliRunner
from app.modules.autonomous_agent.cli import cli


def test_cli_help():
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "KAI Autonomous Agent" in result.output


def test_cli_run_help():
    """Test run command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["run", "--help"])
    assert result.exit_code == 0
    assert "--db" in result.output
    assert "--mode" in result.output
