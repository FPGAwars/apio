"""
  Test for the "apio drivers" command
"""

from test.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.commands.apio import cli as apio


def test_drivers(apio_runner: ApioRunner):
    """Test "apio drivers" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio drivers"
        result = sb.invoke_apio_cmd(apio, "drivers")
        sb.assert_ok(result)
        assert "apio drivers list" in cunstyle(result.output)
        assert "apio drivers install" in cunstyle(result.output)
        assert "apio drivers uninstall" in cunstyle(result.output)
