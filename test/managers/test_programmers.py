"""
Tests of the apio.managers.programmers.py module.
"""

from typing import List
from test.conftest import ApioRunner
from pytest import LogCaptureFixture, raises
from apio.apio_context import ApioContext, ApioContextScope
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
        self,
        usb_devices: List[UsbDevice] = None,
        serial_devices: List[SerialDevice] = None,
    ):
        super().__init__(apio_ctx=None)
        self._usb_devices = usb_devices
        self._serial_devices = serial_devices

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


def fake_usb_device(
    *,
    vid="0403",
    pid="6010",
    bus=0,
    dev=0,
    manuf="AlhambraBits",
    desc="Alhambra II v1.0A",
    sn="SNXXXX",
    device_type="FT2232H",
) -> UsbDevice:
    """Create a fake usb device for resting."""
    # pylint: disable=too-many-arguments
    return UsbDevice(
        vendor_id=vid,
        product_id=pid,
        bus=bus,
        device=dev,
        manufacturer=manuf,
        description=desc,
        serial_number=sn,
        device_type=device_type,
    )


def fake_serial_device(
    *,
    port_name="port0",
    vid="04D8",
    pid="FFEE",
    manuf="IceFUN",
    desc="Ice Fun",
    sn="SNXXXX",
    device_type="FT2232H",
    location="0.1",
) -> UsbDevice:
    """Create a fake serial device for resting."""
    # pylint: disable=too-many-arguments
    return SerialDevice(
        port="/dev/" + port_name,
        port_name=port_name,
        vendor_id=vid,
        product_id=pid,
        manufacturer=manuf,
        description=desc,
        serial_number=sn,
        device_type=device_type,
        location=location,
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

        # -- Create fake devices
        scanner = FakeDeviceScanner(
            usb_devices=[
                fake_usb_device(dev=0, desc="non alhambra"),
                fake_usb_device(dev=1),
                fake_usb_device(dev=2, desc="non alhambra"),
            ],
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

        # -- Check the log.
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
                    "programmer-cmd": "my-programmer ${VID} ${PID}",
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Create fake devices
        scanner = FakeDeviceScanner(
            usb_devices=[
                fake_usb_device(dev=0, desc="non alhambra"),
                fake_usb_device(dev=2, desc="non alhambra"),
            ],
        )

        # -- Call the tested function

        with raises(SystemExit) as e:
            _construct_programmer_cmd(
                apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
            )

        assert e.value.code == 1

        log = capsys.readouterr().out
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
                    "programmer-cmd": "my-programmer ${VID} ${PID}",
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Create fake devices
        scanner = FakeDeviceScanner(
            usb_devices=[
                fake_usb_device(dev=0, sn="SN001"),
                fake_usb_device(dev=1, desc="non alhambra"),
                fake_usb_device(dev=2, sn="SN002"),
            ],
        )

        # -- Call the tested function
        with raises(SystemExit) as e:
            _construct_programmer_cmd(
                apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
            )

        assert e.value.code == 1

        log = capsys.readouterr().out
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


def test_get_cmd_serial(apio_runner: ApioRunner, capsys: LogCaptureFixture):
    """Test generation of a programmer command for a serial device."""
    with apio_runner.in_sandbox() as sb:

        # -- Create a fake apio.ini file.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "icefun",
                    "programmer-cmd": "my-programmer --port ${SERIAL_PORT}",
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Create fake devices
        scanner = FakeDeviceScanner(
            serial_devices=[
                fake_serial_device(port_name="port1", pid="1234"),
                fake_serial_device(port_name="port2"),
                fake_serial_device(port_name="port3", pid="1234"),
            ],
        )

        # -- Call the tested function
        cmd = _construct_programmer_cmd(
            apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
        )

        # -- Test the result programmer command.
        assert cmd == "my-programmer --port /dev/port2"

        # -- Check the log.
        log = capsys.readouterr().out
        assert "Selecting serial device" in log
        assert "FILTER [VID=04D8, PID=FFEE]" in log
        assert (
            "DEVICE [/dev/port2] [04D8:FFEE, [IceFUN] [Ice Fun] [SNXXXX]"
            in log
        )


def test_get_cmd_serial_no_match(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Test command generation error when the serial device is not found."""
    with apio_runner.in_sandbox() as sb:

        # -- Create a fake apio.ini file.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "icefun",
                    "programmer-cmd": "my-programmer --port ${SERIAL_PORT}",
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Create fake devices
        scanner = FakeDeviceScanner(
            serial_devices=[
                fake_serial_device(port_name="port1", pid="1234"),
                fake_serial_device(port_name="port3", pid="1234"),
            ],
        )

        # -- Call the tested function
        with raises(SystemExit) as e:
            _construct_programmer_cmd(
                apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
            )

        assert e.value.code == 1

        log = capsys.readouterr().out
        assert "Selecting serial device" in log
        assert "FILTER [VID=04D8, PID=FFEE]" in log
        assert "Serial device 'icefun' not found" in log


def test_get_cmd_serial_multiple_matches(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Test command generation error when multiple serial devices match the
    filter."""
    with apio_runner.in_sandbox() as sb:

        # -- Create a fake apio.ini file.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "icefun",
                    "programmer-cmd": "my-programmer --port ${SERIAL_PORT}",
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Create fake devices
        scanner = FakeDeviceScanner(
            serial_devices=[
                fake_serial_device(port_name="port1"),
                fake_serial_device(port_name="port2", pid="1234"),
                fake_serial_device(port_name="port3"),
            ],
        )

        # -- Call the tested function
        with raises(SystemExit) as e:
            _construct_programmer_cmd(
                apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
            )

        assert e.value.code == 1

        log = capsys.readouterr().out
        assert "Selecting serial device" in log
        assert "FILTER [VID=04D8, PID=FFEE]" in log
        assert (
            "DEVICE [/dev/port1] [04D8:FFEE, [IceFUN] [Ice Fun] [SNXXXX]"
        ) in log
        assert (
            "DEVICE [/dev/port3] [04D8:FFEE, [IceFUN] [Ice Fun] [SNXXXX]"
        ) in log
        assert "Error: Found multiple matching serial devices" in log


def test_device_presence_ok(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Test generation of a presence check only device."""
    with apio_runner.in_sandbox() as sb:

        # -- Create a fake apio.ini file.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                    # -- The command has no serial or usb vars.
                    "programmer-cmd": "my programmer command ${BIN_FILE}",
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Create fake devices, with two matching devices.
        scanner = FakeDeviceScanner(
            usb_devices=[
                fake_usb_device(dev=0),
                fake_usb_device(dev=1, desc="non alhambra"),
                fake_usb_device(dev=2),
            ],
        )

        # -- Call the tested function
        cmd = _construct_programmer_cmd(
            apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
        )

        # -- Test the result programmer command.
        assert cmd == "my programmer command $SOURCE"

        # -- Check the log.
        log = capsys.readouterr().out
        assert "Checking device presence" in log
        assert 'FILTER [VID=0403, PID=6010, REGEX="^Alhambra II.*"]' in log
        assert (
            "DEVICE [0403:6010, 0:0], [AlhambraBits] "
            "[Alhambra II v1.0A] [SNXXXX]"
        ) in log

        assert (
            "DEVICE [0403:6010, 0:2], [AlhambraBits] "
            "[Alhambra II v1.0A] [SNXXXX]"
        ) in log


def test_device_presence_not_found(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Test generation of a presence only device, with no device."""
    with apio_runner.in_sandbox() as sb:

        # -- Create a fake apio.ini file.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                    # -- The command has no serial or usb vars.
                    "programmer-cmd": "my programmer command ${BIN_FILE}",
                }
            }
        )

        # -- Construct the apio context.
        apio_ctx = ApioContext(scope=ApioContextScope.PROJECT_REQUIRED)

        # -- Create fake devices, with two matching devices.
        scanner = FakeDeviceScanner(
            usb_devices=[
                fake_usb_device(dev=0, desc="non alhambra"),
                fake_usb_device(dev=1, desc="non alhambra"),
            ],
        )

        # -- Call the tested function
        with raises(SystemExit) as e:
            _construct_programmer_cmd(
                apio_ctx, scanner, serial_port_flag=None, serial_num_flag=None
            )

        assert e.value.code == 1

        # -- Check the log.
        log = capsys.readouterr().out
        assert "Checking device presence" in log
        assert 'FILTER [VID=0403, PID=6010, REGEX="^Alhambra II.*"]' in log
        assert "Error: Board 'alhambra-ii' not found" in log
