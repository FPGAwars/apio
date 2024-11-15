"""
  Test for the "apio packages" command
"""

# -- apio packages entry point
from apio.commands.packages import cli as cmd_packages


def test_packages(clirunner, configenv, validate_cliresult):
    """Test "apio packages" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio packages"
        result = clirunner.invoke(cmd_packages)
        assert result.exit_code == 1, result.output
        assert (
            "One of [--list, --install, --uninstall] "
            "must be specified" in result.output
        )

        # -- Execute "apio packages --list"
        result = clirunner.invoke(cmd_packages, ["--list"])
        validate_cliresult(result)

        # -- Execute "apio packages --install missing_package"
        result = clirunner.invoke(
            cmd_packages, ["--install", "missing_package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: no such package" in result.output

        # -- Execute "apio packages --uninstall --sayyes missing_package"
        result = clirunner.invoke(
            cmd_packages, ["--uninstall", "--sayyes", "missing_package"]
        )
        assert result.exit_code == 1, result.output
        assert "Error: no such package" in result.output
