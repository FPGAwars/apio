"""
  Test for the "apio drivers" command
"""

from test.conftest import ApioRunner
from click.termui import unstyle
from apio.commands.apio import cli as apio


def test_drivers(apio_runner: ApioRunner):
    """Test "apio drivers" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio drivers"
        result = sb.invoke_apio_cmd(apio, "drivers")
        sb.assert_ok(result)
        assert "apio drivers list" in unstyle(result.output)
        assert "apio drivers install" in unstyle(result.output)
        assert "apio drivers uninstall" in unstyle(result.output)
