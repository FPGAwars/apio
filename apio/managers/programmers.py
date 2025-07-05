"""DOC: TODO"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import sys
from typing import Optional, List, Dict
from apio.common.apio_console import cout, cerror, cwarning
from apio.common.apio_styles import INFO
from apio.utils import util, serial_util, usb_util
from apio.utils.serial_util import SerialDevice, SerialDeviceFilter
from apio.utils.usb_util import UsbDevice, UsbDeviceFilter
from apio.apio_context import ApioContext

# -- For USB devices
VID_VAR = "${VID}"
PID_VAR = "${PID}"
BUS_VAR = "${BUS}"
DEV_VAR = "${DEV}"
SERIAL_NUM_VAR = "${SERIAL_NUM}"

USB_VARS = [VID_VAR, PID_VAR, BUS_VAR, DEV_VAR, SERIAL_NUM_VAR]

# -- For serial devices.
SERIAL_PORT_VAR = "${SERIAL_PORT}"
SERIAL_VARS = [SERIAL_PORT_VAR]

# -- The ${BIN_FILE} placed holder is replaced here with $SOURCE and later
# -- in scons with the bitstream file path. It can appear in both USB and
# -- serial devices.
BIN_FILE_VAR = "${BIN_FILE}"
BIN_FILE_VALUE = "$SOURCE"

# -- All possible vars.
ALL_VARS = USB_VARS + SERIAL_VARS + [BIN_FILE_VAR]


class _DeviceScanner:
    """Provides usb and serial devices scanning, with caching."""

    def __init__(self, apio_ctx: ApioContext):
        self._apio_ctx: ApioContext = apio_ctx
        self._usb_devices: List[UsbDevice] = None
        self._serial_devices: List[SerialDevice] = None

    def get_usb_devices(self) -> List[UsbDevice]:
        """Scan usb devices, with caching."""
        if self._usb_devices is None:
            self._usb_devices = usb_util.scan_usb_devices(self._apio_ctx)
            assert isinstance(self._usb_devices, list)
        return self._usb_devices

    def get_serial_devices(self) -> List[UsbDevice]:
        """Scan serial devices, with caching."""
        if self._serial_devices is None:
            self._serial_devices = serial_util.scan_serial_devices()
            assert isinstance(self._serial_devices, list)
        return self._serial_devices


def construct_programmer_cmd(
    apio_ctx: ApioContext,
    serial_port_flag: Optional[str],
    serial_num_flag: Optional[str],
) -> str:
    """Construct the programmer command for an 'apio upload' command."""

    # -- This is a thin wrapper to allow injecting test scanners in tests.
    scanner = _DeviceScanner(apio_ctx)
    return _construct_programmer_cmd(
        apio_ctx, scanner, serial_port_flag, serial_num_flag
    )


def _construct_programmer_cmd(
    apio_ctx: ApioContext,
    scanner: _DeviceScanner,
    serial_port_flag: Optional[str],
    serial_num_flag: Optional[str],
) -> str:
    """Construct the programmer command for an 'apio upload' command."""

    # -- Construct the programmer cmd template for the board. It may or may not
    # -- contain ${} vars.
    cmd_template = _construct_cmd_template(apio_ctx)
    if util.is_debug(1):
        cout(f"Cmd template: [{cmd_template}]")

    # -- Resolved the mandatory ${BIN_FILE} to $SOURCE which will be replaced
    # -- by scons with the path of the bitstream file.
    cmd_template = cmd_template.replace(BIN_FILE_VAR, BIN_FILE_VALUE)

    # -- Determine how to resolve this template.
    has_usb_vars = any(s in cmd_template for s in USB_VARS)
    has_serial_vars = any(s in cmd_template for s in SERIAL_VARS)

    if util.is_debug(1):
        cout(f"Template has usb vars: {has_usb_vars}]")
        cout(f"Template has serial vars: {has_serial_vars}]")

    # -- Can't have both serial and usb vars (OK to have none).
    if has_usb_vars and has_serial_vars:
        board = apio_ctx.project.get_str_option("board")
        cerror(
            f"The programmer cmd template of the board '{board}' has "
            "both usb and serial ${} vars. "
        )
        cout(f"Cmd template: {cmd_template}", style=INFO)
        sys.exit(1)

    # -- Dispatch to the appropriate template resolver.
    if has_serial_vars:
        cmd = _resolve_serial_cmd_template(
            apio_ctx, scanner, serial_port_flag, serial_num_flag, cmd_template
        )

    elif has_usb_vars:
        _report_unused_flag("--serial-port", serial_port_flag)
        cmd = _resolve_usb_cmd_template(
            apio_ctx, scanner, serial_num_flag, cmd_template
        )

    else:
        # -- If there are no vars to resolve, we don't need to match to a
        # -- specific usb or serial device but just to check that if the board
        # -- has 'usb' section, there is at least one device that matchs the
        # -- constraints in that section.
        _report_unused_flag("--serial-port", serial_port_flag)
        _report_unused_flag("--serial-num", serial_num_flag)
        _check_device_presence(apio_ctx, scanner)

        # -- Template has no vars, we just use it as is.
        cmd = cmd_template

    # -- At this point, all vars should be resolved.
    assert not any(s in cmd for s in ALL_VARS), cmd_template

    # -- Return the resolved command.
    return cmd


def _report_unused_flag(flag_name: str, flag_value: str):
    """If flag_value is not falsy then print a warning message."""
    if flag_value:
        cwarning(f"{flag_name} ignored.")


def _construct_cmd_template(apio_ctx: ApioContext) -> str:
    """Construct a command template for the board.
    Example:
       "openFPGAloader --verify -b ice40_generic --vid ${VID} --pid ${PID}
       --busdev-num ${BUS}:${DEV} ${BIN_FILE}"
    """

    # -- If the project file has a custom programmer command use it instead
    # -- of the standard definitions.
    custom_template = apio_ctx.project.get_str_option("programmer-cmd")
    if custom_template:
        cout("Using custom programmer cmd.")
        if BIN_FILE_VALUE in custom_template:
            cerror(
                f"Custom programmer-cmd should not contain '{BIN_FILE_VALUE}'."
            )
            sys.exit(1)
        return custom_template

    pr = apio_ctx.project_resources
    # -- Here when using the standard command.

    # -- Start building the template with the programmer binary name.
    # -- E.g. "openFPGAloader". "command" is a validated required field.
    cmd_template = pr.programmer_info["command"]

    # -- Append the optional args template from the programmer.
    args = pr.programmer_info.get("args", "")
    if args:
        cmd_template += " "
        cmd_template += args

    # -- Append the optional extra args template from the board.
    extra_args = pr.board_info["programmer"].get("extra-args", "")
    if extra_args:
        cmd_template += " "
        cmd_template += extra_args

    # -- Append the bitstream file placeholder if its' not already in the
    # -- template.
    if BIN_FILE_VAR not in cmd_template:
        cmd_template += " "
        cmd_template += BIN_FILE_VAR

    # -- All done.
    return cmd_template


def _resolve_serial_cmd_template(
    apio_ctx: ApioContext,
    scanner: _DeviceScanner,
    serial_port_arg: Optional[str],
    serial_port_num: Optional[str],
    cmd_template: str,
) -> str:
    """Resolves a programmer command template for a serial device."""

    # -- Match to a single serial device.
    device: SerialDevice = _match_serial_device(
        apio_ctx, scanner, serial_port_arg, serial_port_num
    )

    # -- Resolve serial port var.
    cmd_template = cmd_template.replace(SERIAL_PORT_VAR, device.port)

    # -- Sanity check, should have no serial vars unresolved.
    assert not any(s in cmd_template for s in SERIAL_VARS), cmd_template

    # -- All done.
    return cmd_template


def _resolve_usb_cmd_template(
    apio_ctx: ApioContext,
    scanner: _DeviceScanner,
    serial_num_flag: Optional[str],
    cmd_template: str,
) -> str:
    """Resolves a programmer command template for an USB device."""

    # -- Match to a single usb device.
    device: UsbDevice = _match_usb_device(apio_ctx, scanner, serial_num_flag)

    # -- Substitute vars.
    cmd_template = cmd_template.replace(VID_VAR, device.vendor_id)
    cmd_template = cmd_template.replace(PID_VAR, device.product_id)
    cmd_template = cmd_template.replace(BUS_VAR, str(device.bus))
    cmd_template = cmd_template.replace(DEV_VAR, str(device.device))
    cmd_template = cmd_template.replace(SERIAL_NUM_VAR, device.serial_number)

    # -- Sanity check, should have no usb vars unresolved.
    assert not any(s in cmd_template for s in USB_VARS), cmd_template

    # -- All done.
    return cmd_template


def _match_serial_device(
    apio_ctx: ApioContext,
    scanner: _DeviceScanner,
    serial_port_flag: Optional[str],
    serial_num_flag: Optional[str],
) -> SerialDevice:
    """Scans the serial devices and selects and returns a single matching
    device. Exits with an error if none or multiple matching devices.
    """

    # -- Get project resources
    pr = apio_ctx.project_resources

    # -- Scan for all serial devices.
    all_devices: List[SerialDevice] = scanner.get_serial_devices()

    # -- Get board optional usb constraints
    usb_info = pr.board_info.get("usb", {})

    # -- Construct a device filter.
    serial_filter = SerialDeviceFilter()
    if "vid" in usb_info:
        serial_filter.set_vendor_id(usb_info["vid"].upper())
    if "pid" in usb_info:
        serial_filter.set_product_id(usb_info["pid"].upper())
    if "product-regex" in usb_info:
        serial_filter.set_product_regex(usb_info["product-regex"])
    if serial_port_flag:
        serial_filter.set_port(serial_port_flag)
    if serial_num_flag:
        serial_filter.set_serial_num(serial_num_flag)

    # -- Inform the user.
    cout("Scanning for a serial device:")
    cout(f"- FILTER {serial_filter.summary()}")

    # -- Get matching devices
    matching: List[SerialDevice] = serial_filter.filter(all_devices)

    for dev in matching:
        cout(f"- DEVICE {dev.summary()}")

    if util.is_debug(1):
        cout(f"Serial device filter: {serial_filter.summary()}")
        cout(f"Matching serial devices: {matching}")

    if util.is_debug(1):
        cout(f"Matching serial devices: {matching}")

    # -- Error if not exactly one match.
    if not matching:
        cerror("No matching serial device.")
        cout(
            "Type 'apio devices serial' for available serial devices.",
            style=INFO,
        )
        sys.exit(1)

    # -- Error more than one match
    if len(matching) > 1:
        cerror("Found multiple matching serial devices.")
        cout(
            "Type 'apio devices serial' for available serial devices.",
            style=INFO,
        )
        sys.exit(1)

    # -- All done. We have a single match.
    return matching[0]


def _match_usb_device(
    apio_ctx: ApioContext, scanner, serial_num_flag: Optional[str]
) -> UsbDevice:
    """Scans the USB devices and selects and returns a single matching
    device. Exits with an error if none or multiple matching devices.
    """

    # -- Get project resources.
    pr = apio_ctx.project_resources

    # -- Scan for all serial devices.
    all_devices: List[UsbDevice] = scanner.get_usb_devices()

    # -- Get board optional usb constraints
    usb_info = pr.board_info.get("usb", {})

    # -- Construct a device filter.
    usb_filter = UsbDeviceFilter()
    if "vid" in usb_info:
        usb_filter.set_vendor_id(usb_info["vid"].upper())
    if "pid" in usb_info:
        usb_filter.set_product_id(usb_info["pid"].upper())
    if "product-regex" in usb_info:
        usb_filter.set_product_regex(usb_info["product-regex"])
    if serial_num_flag:
        usb_filter.set_serial_num(serial_num_flag)

    # -- Inform the user.
    cout("Scanning for a USB device:")
    cout(f"- FILTER {usb_filter.summary()}")

    # -- Get matching devices
    matching: List[UsbDevice] = usb_filter.filter(all_devices)

    for dev in matching:
        cout(f"- DEVICE {dev.summary()}")

    if util.is_debug(1):
        cout(f"USB device filter: {usb_filter.summary()}")
        cout(f"Matching USB devices: {matching}")

    if util.is_debug(1):
        cout(f"Matching usb devices: {matching}")

    # -- Error if not exactly one match.
    if not matching:
        cerror("No matching USB device.")
        cout(
            "Type 'apio devices usb' for available usb devices.",
            style=INFO,
        )
        sys.exit(1)

    # -- Error more than one match
    if len(matching) > 1:
        cerror("Found multiple matching usb devices.")
        cout(
            "Type 'apio devices usb' for available usb device.",
            style=INFO,
        )
        sys.exit(1)

    # -- All done. We have a single match.
    return matching[0]


def _check_device_presence(apio_ctx: ApioContext, scanner: _DeviceScanner):
    """If the board info has a "usb" section, check that there is at least one
    usb device that matches the constraints, if any, in the "usb" section.
    Returns if OK, exits with an error otherwise.
    """

    # -- Get project resources.
    pr = apio_ctx.project_resources

    # -- Get the optional "usb" section of the board.
    usb_info: Dict[str, str] = pr.board_info.get("usb", None)

    # -- If no "usb" section there are no constrained to check. We don't
    # -- even check that any usb device exists.
    if usb_info is None:
        return

    # -- Create a device filter with the constraints. Note that the "usb"
    # -- section may contain no constrained which will result in a pass-all
    # -- filter.
    usb_filter = UsbDeviceFilter()
    if "vid" in usb_info:
        usb_filter.set_vendor_id(usb_info["vid"].upper())
    if "pid" in usb_info:
        usb_filter.set_product_id(usb_info["pid"].upper())
    if "product-regex" in usb_info:
        usb_filter.set_product_regex(usb_info["product-regex"])

    cout("Checking device presence...")
    cout(f"- FILTER {usb_filter.summary()}")

    # -- Scan the USB devices and filter by the filter.
    all_devices = scanner.get_usb_devices()
    matching_devices = usb_filter.filter(all_devices)

    for device in matching_devices:
        cout(f"- DEVICE {device.summary()}")

    # -- If no device passed the filter fail the check.
    if not matching_devices:
        cerror("No matching device.")
        cout(
            "Type 'apio devices usb' for available usb devices.",
            style=INFO,
        )
        sys.exit(1)

    # -- All OK.
