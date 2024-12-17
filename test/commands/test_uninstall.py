"""
  Test for the "apio uninstall" command
"""

from test.conftest import ApioRunner

# -- apio uninstall entry point
from apio.commands.uninstall import cli as apio_uninstall


def test_uninstall(apio_runner: ApioRunner):
    """Test "apio uninstall" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio uninstall"
        result = sb.invoke_apio_cmd(apio_uninstall)
        sb.assert_ok(result)

        # -- Execute "apio uninstall --list"
        result = sb.invoke_apio_cmd(apio_uninstall, ["--list"])
        sb.assert_ok(result)

        # -- Execute "apio uninstall missing_packge"
        result = sb.invoke_apio_cmd(
            apio_uninstall, ["missing_package"], input="y"
        )
        assert result.exit_code == 1, result.output
        assert "Do you want to uninstall?" in result.output
        assert "Error: no such package" in result.output
