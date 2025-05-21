"""Test for the "apio devices" command."""

from test.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.commands.apio import cli as apio


def test_devices(apio_runner: ApioRunner):
    """Test "apio devices" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio devices"
        result = sb.invoke_apio_cmd(apio, "devices")
        sb.assert_ok(result)
        assert "apio devices ftdi" in cunstyle(result.output)
        assert "apio devices usb" in cunstyle(result.output)
        assert "apio devices serial" in cunstyle(result.output)
