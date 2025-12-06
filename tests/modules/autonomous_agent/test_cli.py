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


def test_cli_mdl_list_help():
    """Test mdl-list command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["mdl-list", "--help"])
    assert result.exit_code == 0
    assert "List MDL semantic layer manifests" in result.output


def test_cli_mdl_show_help():
    """Test mdl-show command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["mdl-show", "--help"])
    assert result.exit_code == 0
    assert "Show details of an MDL manifest" in result.output


def test_cli_mdl_export_help():
    """Test mdl-export command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["mdl-export", "--help"])
    assert result.exit_code == 0
    assert "Export MDL manifest" in result.output
    assert "--output" in result.output
    assert "-o" in result.output


def test_cli_mdl_delete_help():
    """Test mdl-delete command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["mdl-delete", "--help"])
    assert result.exit_code == 0
    assert "Delete an MDL manifest" in result.output
    assert "--force" in result.output
