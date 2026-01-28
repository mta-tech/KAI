from click.testing import CliRunner
from app.modules.autonomous_agent.main import cli


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


# ============================================================================
# Config Group Tests
# ============================================================================

def test_config_group_help():
    """Test config group help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "--help"])
    assert result.exit_code == 0
    assert "Configuration and system utilities" in result.output
    assert "show" in result.output
    assert "check" in result.output
    assert "version" in result.output
    assert "worker" in result.output


def test_config_show_help():
    """Test config show command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "show", "--help"])
    assert result.exit_code == 0
    assert "Show current configuration settings" in result.output
    assert "--json" in result.output


def test_config_check_help():
    """Test config check command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "check", "--help"])
    assert result.exit_code == 0
    assert "Check environment variables and API keys" in result.output


def test_config_version_help():
    """Test config version command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "version", "--help"])
    assert result.exit_code == 0
    assert "Show KAI Agent version information" in result.output


def test_config_version_output():
    """Test config version command output."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "version"])
    assert result.exit_code == 0
    assert "KAI Agent" in result.output
    assert "LangGraph" in result.output or "version" in result.output.lower()


def test_config_worker_help():
    """Test config worker command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["config", "worker", "--help"])
    assert result.exit_code == 0
    assert "Start the KAI Temporal Worker" in result.output


# ============================================================================
# Connection Group Tests
# ============================================================================

def test_connection_group_help():
    """Test connection group help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["connection", "--help"])
    assert result.exit_code == 0
    assert "Database connection management" in result.output
    assert "create" in result.output
    assert "list" in result.output
    assert "show" in result.output
    assert "update" in result.output
    assert "delete" in result.output
    assert "test" in result.output


def test_connection_create_help():
    """Test connection create command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["connection", "create", "--help"])
    assert result.exit_code == 0
    assert "Create a new database connection" in result.output
    assert "--alias" in result.output or "-a" in result.output
    assert "--schema" in result.output or "-s" in result.output


def test_connection_list_help():
    """Test connection list command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["connection", "list", "--help"])
    assert result.exit_code == 0
    assert "List available database connections" in result.output


def test_connection_show_help():
    """Test connection show command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["connection", "show", "--help"])
    assert result.exit_code == 0
    assert "Show details of a database connection" in result.output
    assert "CONNECTION_ID" in result.output


def test_connection_update_help():
    """Test connection update command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["connection", "update", "--help"])
    assert result.exit_code == 0
    assert "Update an existing database connection" in result.output
    assert "--alias" in result.output or "-a" in result.output


def test_connection_delete_help():
    """Test connection delete command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["connection", "delete", "--help"])
    assert result.exit_code == 0
    assert "Delete a database connection" in result.output
    assert "--force" in result.output or "-f" in result.output


def test_connection_test_help():
    """Test connection test command help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["connection", "test", "--help"])
    assert result.exit_code == 0
    assert "Test a database connection without saving it" in result.output


# ============================================================================
# CLI Structure Tests
# ============================================================================

def test_cli_has_config_group():
    """Test that CLI has config group registered."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "config" in result.output
    # Old commands should not be at top level
    assert "env-check" not in result.output


def test_cli_has_connection_group():
    """Test that CLI has connection group registered."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "connection" in result.output
    # Old commands should not be at top level
    assert "create-connection" not in result.output
    assert "list-connections" not in result.output
    assert "show-connection" not in result.output
    assert "update-connection" not in result.output
    assert "delete-connection" not in result.output
    assert "test-connection" not in result.output


def test_cli_has_mdl_group():
    """Test that CLI has mdl group registered."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "mdl" in result.output


def test_old_commands_not_available():
    """Test that old flat commands are not available (breaking change)."""
    runner = CliRunner()
    
    # These old commands should fail
    old_commands = [
        ["config"],
        ["env-check"],
        ["version"],
        ["create-connection"],
        ["list-connections"],
        ["show-connection", "test_id"],
        ["update-connection", "test_id"],
        ["delete-connection", "test_id"],
        ["test-connection", "test_uri"],
    ]
    
    for cmd in old_commands:
        result = runner.invoke(cli, cmd)
        # Should either fail or not be recognized
        assert result.exit_code != 0 or "No such command" in result.output
