"""
  Test for the "apio uninstall" command
"""

from test.conftest import ApioRunner

# -- apio uninstall entry point
from apio.commands.uninstall import cli as apio_uninstall


def test_uninstall(apio_runner: ApioRunner):
    """Test "apio uninstall" with different parameters"""

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment
        apio_runner.setup_env()

        # -- Execute "apio uninstall"
        result = apio_runner.invoke(apio_uninstall)
        apio_runner.assert_ok(result)

        # -- Execute "apio uninstall --list"
        result = apio_runner.invoke(apio_uninstall, ["--list"])
        apio_runner.assert_ok(result)

        # -- Execute "apio uninstall missing_packge"
        result = apio_runner.invoke(
            apio_uninstall, ["missing_package"], input="y"
        )
        assert result.exit_code == 1, result.output
        assert "Do you want to uninstall?" in result.output
        assert "Error: no such package" in result.output
