"""
  Test for the "apio uninstall" command
"""

# -- apio uninstall entry point
from apio.commands.uninstall import cli as apio_uninstall


def test_uninstall(click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok):
    """Test "apio uninstall" with different parameters"""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio uninstall"
        result = click_cmd_runner.invoke(apio_uninstall)
        assert_apio_cmd_ok(result)

        # -- Execute "apio uninstall --list"
        result = click_cmd_runner.invoke(apio_uninstall, ["--list"])
        assert_apio_cmd_ok(result)

        # -- Execute "apio uninstall missing_packge"
        result = click_cmd_runner.invoke(
            apio_uninstall, ["missing_package"], input="y"
        )
        assert result.exit_code == 1, result.output
        assert "Do you want to uninstall?" in result.output
        assert "Error: no such package" in result.output
