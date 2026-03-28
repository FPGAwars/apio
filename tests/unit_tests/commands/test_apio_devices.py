"""Test for the "apio devices" command."""

from tests.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.commands.apio import apio_top_cli as apio


def test_devices(apio_runner: ApioRunner):
    """Test "apio devices" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio devices"
        result = sb.invoke_apio_cmd(apio, ["devices"])
        sb.assert_result_ok(result)
        assert "apio devices scan-usb" in cunstyle(result.output)
        assert "apio devices scan-serial" in cunstyle(result.output)


def test_apio_devices(apio_runner: ApioRunner):
    """Test "apio devices scan-usb|serial" """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio devices scan-usb". We run it in a
        # -- subprocess such that it releases the libusb1 file it uses.
        # -- This also means that it's not included in the pytest test
        # -- coverage report.
        result = sb.invoke_apio_cmd(
            apio, ["devices", "scan-usb"], in_subprocess=True
        )
        sb.assert_result_ok(result)
        print(result.output)

        # -- Execute "apio devices scan-serial". We run it in a
        # -- subprocess such that it releases the libusb1 file it uses.
        # -- This also means that it's not included in the pytest test
        # -- coverage report.
        result = sb.invoke_apio_cmd(
            apio, ["devices", "scan-serial"], in_subprocess=True
        )
        sb.assert_result_ok(result)
        print(result.output)
