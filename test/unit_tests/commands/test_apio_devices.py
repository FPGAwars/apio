"""Test for the "apio devices" command."""

from test.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.commands.apio import apio_top_cli as apio


def test_devices(apio_runner: ApioRunner):
    """Test "apio devices" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio devices"
        result = sb.invoke_apio_cmd(apio, ["devices"])
        sb.assert_ok(result)
        assert "apio devices usb" in cunstyle(result.output)
        assert "apio devices serial" in cunstyle(result.output)


def test_apio_devices(apio_runner: ApioRunner):
    """Test "apio devices usb|serial" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio devices usb". We run it in a
        # -- subprocess such that it releases the libusb1 file it uses.
        result = sb.invoke_apio_cmd(
            apio, ["devices", "usb"], in_subprocess=True
        )
        sb.assert_ok(result)
        print(result.output)

        # -- Execute "apio devices serial". We run it in a
        # -- subprocess such that it releases the libusb1 file it uses.
        result = sb.invoke_apio_cmd(
            apio, ["devices", "serial"], in_subprocess=True
        )
        sb.assert_ok(result)
        print(result.output)
