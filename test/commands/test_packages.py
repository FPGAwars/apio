"""
  Test for the "apio packages" command
"""

# -- apio packages entry point
from apio.commands.packages import cli as apio_packages


def test_packages(click_cmd_runner, setup_apio_test_env):
    """Test "apio packages" with different parameters"""

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio packages"
        result = click_cmd_runner.invoke(apio_packages)
        assert result.exit_code == 1, result.output
        assert (
            "One of [--list, --install, --uninstall, --fix] "
            "must be specified" in result.output
        )

        # -- Execute "apio packages --list"
        result = click_cmd_runner.invoke(apio_packages, ["--list"])
        assert result.exit_code == 0, result.output
        assert "No errors" in result.output

        # -- Execute "apio packages --install missing_package"
        result = click_cmd_runner.invoke(
            apio_packages, ["--install", "missing_package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: unknown package 'missing_package'" in result.output

        # -- Execute "apio packages --uninstall --sayyes missing_package"
        result = click_cmd_runner.invoke(
            apio_packages, ["--uninstall", "--sayyes", "missing_package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: no such package 'missing_package'" in result.output
