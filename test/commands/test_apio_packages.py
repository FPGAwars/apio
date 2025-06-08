"""Test for the "apio packages" command."""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio
from apio.common.apio_console import cunstyle


def test_packages(apio_runner: ApioRunner):
    """Test "apio packages" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio packages"
        result = sb.invoke_apio_cmd(apio, ["packages"])
        sb.assert_ok(result)
        assert "Subcommands:" in result.output
        assert "apio packages update" in cunstyle(result.output)
        assert "apio packages list" in cunstyle(result.output)
        assert result.output != cunstyle(result.output)  # Colored.

        # -- Execute "apio packages list"
        result = sb.invoke_apio_cmd(apio, ["packages", "list"])
        sb.assert_ok(result)
