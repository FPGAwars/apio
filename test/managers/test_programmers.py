"""
Tests of the apio.managers.programmers.py module.
"""

from typing import List
from apio.apio_context import ApioContext, ApioContextScope
from test.conftest import ApioRunner
from pytest import LogCaptureFixture, raises
from apio.utils.usb_util import UsbDevice
from apio.utils.serial_util import SerialDevice

from apio.managers.programmers import (
    _construct_cmd_template,
    _construct_programmer_cmd,
    _DeviceScanner,
)


class FakeDeviceScanner(_DeviceScanner):
    """A fake device scanner for testing."""

    def __init__(
        self, usb_devices: List[UsbDevice], serial_devices: List[SerialDevice]
    ):
        self._usb_devices = usb_devices
        self._serial_devices = serial_devices
        pass

    # @override
    def get_usb_devices(self) -> List[UsbDevice]:
        """Returns the fake usb devices."""
        assert self._usb_devices
        return self._usb_devices

    # @override
    def get_serial_devices(self) -> List[UsbDevice]:
        """Returns the fake serial devices."""
        assert self._serial_devices
        return self._serial_devices


def fake_usb_board(
    *,
    bus=0,
    dev=0,
    vid="0403",
    pid="6010",
    manuf="AlhambraBits",
    desc="Alhambra II v1.0A",
    sn="SNXXXX",
    type="FT2232H",
) -> UsbDevice:
    """Create a fake usb device for resting."""
    return UsbDevice(
        bus=bus,
        device=dev,
        vendor_id=vid,
        product_id=pid,
        manufacturer=manuf,
        description=desc,
        serial_number=sn,
        device_type=type,
    )


def test_default_cmd_template(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests _construct_cmd_template() with the default board template."""

    with apio_runner.in_sandbox() as sb:

        # -- Construct an apio context.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                    "top-module": "my_module",
                }
            }
        )

        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)
        programmer_cmd = _construct_cmd_template(apio_ctx)

        # -- Check result.
        assert (
            programmer_cmd == "openFPGALoader --verify -b ice40_generic "
            "--vid ${VID} --pid ${PID} "
            "--busdev-num ${BUS}:${DEV} "
            "${BIN_FILE}"
        )

        # -- Check no 'custom' warning.
        assert "Using custom programmer cmd" not in capsys.readouterr().out


def test_custom_cmd_template(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Tests _construct_cmd_template() with custom command template."""

    with apio_runner.in_sandbox() as sb:

        # -- Construct an apio context.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                    "top-module": "my_module",
                    "programmer-cmd": "my template ${VID} ${PID}",
                }
            }
        )

        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)
        programmer_cmd = _construct_cmd_template(apio_ctx)

        # -- Check the result.
        assert programmer_cmd == "my template ${VID} ${PID}"

        # -- Check the 'custom' warning.
        assert "Using custom programmer cmd" in capsys.readouterr().out


def test_get_cmd_usb(apio_runner: ApioRunner, capsys: LogCaptureFixture):
    """Test generation of a programmer command for a usb device."""
    with apio_runner.in_sandbox() as sb:

        # -- Create a fake apio.ini file.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                    "top-module": "my_module",
                    "programmer-cmd": (
                        "my-programmer --bus ${BUS} --dev ${DEV} "
                        "--vid ${VID} --pid ${PID} "
                        "--serial-num ${SERIAL_NUM} --bin-file ${BIN_FILE}"
                    ),
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Create a fake device scanner. Trying to scan for serial devices
        # -- will fail on an assertion.
        scanner = FakeDeviceScanner(
            usb_devices=[
                fake_usb_board(dev=0, desc="non alhambra"),
                fake_usb_board(dev=1),
                fake_usb_board(dev=2, desc="non alhambra"),
            ],
            serial_devices=None,
        )

        # -- Call the tested function
        cmd = _construct_programmer_cmd(
            apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
        )

        # -- Test the result programmer command.
        assert cmd == (
            "my-programmer --bus 0 --dev 1 --vid 0403 --pid 6010 "
            "--serial-num SNXXXX --bin-file $SOURCE"
        )

        # -- Test the log.
        log = capsys.readouterr().out
        assert "Selecting USB device" in log
        assert 'FILTER [VID=0403, PID=6010, REGEX="^Alhambra II.*"]' in log
        assert (
            "DEVICE [0403:6010, 0:1], [AlhambraBits] "
            "[Alhambra II v1.0A] [SNXXXX]"
        ) in log


def test_get_cmd_usb_no_match(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Test command generation error when the usb device is not found."""
    with apio_runner.in_sandbox() as sb:

        # -- Create a fake apio.ini file.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                    "top-module": "my_module",
                    "programmer-cmd": "my-programmer ${VID} ${PID}",
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Create fake usb devices that don't match alhambra's II
        # -- description regex.
        scanner = FakeDeviceScanner(
            usb_devices=[
                fake_usb_board(dev=0, desc="non alhambra"),
                fake_usb_board(dev=2, desc="non alhambra"),
            ],
            serial_devices=None,
        )

        # -- Call the tested function

        with raises(SystemExit) as e:
            _construct_programmer_cmd(
                apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
            )

        assert e.value.code == 1

        log = capsys.readouterr().out
        assert "" in log
        assert "Selecting USB device" in log
        assert 'FILTER [VID=0403, PID=6010, REGEX="^Alhambra II.*"]' in log
        assert "USB board 'alhambra-ii' not found" in log


def test_get_cmd_usb_multiple_matches(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Test command generation error when multiple usb devices match the
    filter."""
    with apio_runner.in_sandbox() as sb:

        # -- Create a fake apio.ini file.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                    "top-module": "my_module",
                    "programmer-cmd": "my-programmer ${VID} ${PID}",
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Two usb devices matches the filter.
        scanner = FakeDeviceScanner(
            usb_devices=[
                fake_usb_board(dev=0, sn="SN001"),
                fake_usb_board(dev=1, desc="non alhambra"),
                fake_usb_board(dev=2, sn="SN002"),
            ],
            serial_devices=None,
        )

        # -- Call the tested function

        with raises(SystemExit) as e:
            _construct_programmer_cmd(
                apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
            )

        assert e.value.code == 1

        log = capsys.readouterr().out
        assert "" in log
        assert "Selecting USB device" in log
        assert 'FILTER [VID=0403, PID=6010, REGEX="^Alhambra II.*"]' in log
        assert (
            "DEVICE [0403:6010, 0:0], [AlhambraBits] "
            "[Alhambra II v1.0A] [SN001]"
        ) in log
        assert (
            "DEVICE [0403:6010, 0:2], [AlhambraBits] "
            "[Alhambra II v1.0A] [SN002]"
        ) in log
        assert "Error: Found multiple matching usb devices" in log
