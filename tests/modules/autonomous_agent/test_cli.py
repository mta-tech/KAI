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


def test_cli_scan_all_help():
    """Test scan-all command help shows MDL options."""
    runner = CliRunner()
    result = runner.invoke(cli, ["scan-all", "--help"])
    assert result.exit_code == 0
    assert "--generate-mdl" in result.output or "-m" in result.output
    assert "--mdl-name" in result.output
    assert "MDL semantic layer" in result.output


def test_cli_scan_all_mdl_option_documented():
    """Test scan-all command documents MDL generation examples."""
    runner = CliRunner()
    result = runner.invoke(cli, ["scan-all", "--help"])
    assert result.exit_code == 0
    # Check that MDL examples are in the help text
    assert "--generate-mdl" in result.output
    assert "semantic layer" in result.output.lower()
