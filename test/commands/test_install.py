"""
  Test for the "apio install" command
"""

# -- apio install entry point
from apio.commands.install import cli as apio_install


def test_install(click_cmd_runner, setup_apio_test_env, assert_apio_cmd_ok):
    """Test "apio install" with different parameters"""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio install"
        result = click_cmd_runner.invoke(apio_install)
        assert_apio_cmd_ok(result)

        # -- Execute "apio install --list"
        result = click_cmd_runner.invoke(apio_install, ["--list"])
        assert_apio_cmd_ok(result)

        # -- Execute "apio install missing_package"
        result = click_cmd_runner.invoke(apio_install, ["missing_package"])
        assert result.exit_code == 1, result.output
        assert "Error: no such package" in result.output
