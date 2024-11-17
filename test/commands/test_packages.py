"""
  Test for the "apio packages" command
"""

# -- apio packages entry point
from apio.commands.packages import cli as cmd_packages


def test_packages(clirunner, configenv):
    """Test "apio packages" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio packages"
        result = clirunner.invoke(cmd_packages)
        assert result.exit_code == 1, result.output
        assert (
            "One of [--list, --install, --uninstall, --fix] "
            "must be specified" in result.output
        )

        # -- Execute "apio packages --list"
        result = clirunner.invoke(cmd_packages, ["--list"])
        assert result.exit_code == 0, result.output
        assert "No errors" in result.output

        # -- Execute "apio packages --install missing_package"
        result = clirunner.invoke(
            cmd_packages, ["--install", "missing_package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: unknown package 'missing_package'" in result.output

        # -- Execute "apio packages --uninstall --sayyes missing_package"
        result = clirunner.invoke(
            cmd_packages, ["--uninstall", "--sayyes", "missing_package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: no such package 'missing_package'" in result.output
