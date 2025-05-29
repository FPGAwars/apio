"""DOC: TODO"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2

import sys
from typing import Optional, List, Dict
from apio.common.apio_console import cout, cerror
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

# -- For all devices.
ALL_VARS = USB_VARS + SERIAL_VARS


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
    serial_port_arg: Optional[str],
) -> str:
    """Construct the programmer command for an 'apio upload' command."""

    # -- This is a thin wrapper to allow injecting test scanners in tests.
    scanner = _DeviceScanner(apio_ctx)
    return _construct_programmer_cmd(apio_ctx, scanner, serial_port_arg)


def _construct_programmer_cmd(
    apio_ctx: ApioContext,
    scanner: _DeviceScanner,
    serial_port_arg: Optional[str],
) -> str:
    """Construct the programmer command for an 'apio upload' command."""

    # -- If the board info has a "usb" section, check that there is at least
    # -- one usb device that meets those constrained. Note that this may apply
    # -- also to devices that are resolved below as 'serial'.
    _check_device_presence(apio_ctx, scanner)

    # -- Construct the programmer cmd template for the board. It may or may not
    # -- contain ${} vars.
    cmd_template = _construct_cmd_template(apio_ctx)
    if util.is_debug():
        cout(f"Programmer template: [{cmd_template}]")

    # -- The placeholder for the bitstream file name should always exist. This
    # -- placeholder is resolved later in scons.
    assert "$SOURCE" in cmd_template, cmd_template

    # -- Determine how to resolve this template.
    has_usb_vars = any(s in cmd_template for s in USB_VARS)
    has_serial_vars = any(s in cmd_template for s in SERIAL_VARS)

    # -- Can't have both serial and usb vars (OK to have none).
    if has_usb_vars and has_serial_vars:
        board = apio_ctx.project["board"]
        cerror(
            f"The programmer cmd template of the board '{board}' has "
            "both usb and serial ${} vars. "
        )
        cout(f"Cmd template: {cmd_template}", style=INFO)
        sys.exit(1)

    # -- Dispatch to the appropriate template resolver.
    if has_serial_vars:
        cmd = _resolve_serial_cmd_template(
            apio_ctx, scanner, serial_port_arg, cmd_template
        )

    elif has_usb_vars:
        cmd = _resolve_usb_cmd_template(apio_ctx, scanner, cmd_template)

    else:
        # -- Template has no vars, no need to resolve.
        cmd = cmd_template

    # -- At this point, all vars should be resolved.
    assert not any(s in cmd for s in ALL_VARS), cmd_template

    # -- The placeholder for the bitstream file name should always exist.
    assert "$SOURCE" in cmd, cmd

    # -- Return the resolved command.
    return cmd


def _check_device_presence(apio_ctx: ApioContext, scanner: _DeviceScanner):
    """If the board info has a "usb" section, check that there is at least one
    usb device that matches the constraints, if any, in the "usb" section.
    Returns if OK, exits with an error otherwise.
    """

    # -- Get board info
    board = apio_ctx.project["board"]
    board_info = apio_ctx.boards[board]

    # -- Get the optional "usb" section
    usb_info: Dict[str, str] = board_info.get("usb", None)

    # -- If no "usb" section there are no constrained to check.
    if usb_info is None:
        return

    # -- Create a device filter with the constraints. Note that the "usb"
    # -- section may contain no constrained which will result in a pass-all
    # -- filter.
    filt = UsbDeviceFilter()
    if "vid" in usb_info:
        filt.vendor_id(usb_info["vid"])
    if "pid" in usb_info:
        filt.product_id(usb_info["pid"])
    if "desc-regex" in usb_info:
        filt.desc_regex(usb_info["desc-regex"])

    # -- Scan the USB devices and filter by the filter.
    all_devices = scanner.get_usb_devices()
    matching_devices = filt.filter(all_devices)

    # -- If no device passed the filter fail the check.
    if not matching_devices:
        cerror(f"Board '{board}' not found.")
        cout(
            "Type 'apio devices usb' to list the usb devices.",
            f"Filter used: {str(filt)}",
            style=INFO,
        )
        sys.exit(1)

    # -- All OK.


def _resolve_serial_cmd_template(
    apio_ctx: ApioContext,
    scanner: _DeviceScanner,
    serial_port_arg: Optional[str],
    cmd_template: str,
) -> str:
    """Resolves a programmer command template for a serial device."""

    # -- Match to a single serial device.
    device: SerialDevice = _match_serial_device(
        apio_ctx, scanner, serial_port_arg
    )

    # -- Resolve serial port var.
    cmd_template = cmd_template.replace(SERIAL_PORT_VAR, device.port)

    # -- Sanity check, should have no serial vars unresolved.
    # assert not any(s in template for s in SERIAL_VARS), template

    # -- All done.
    return cmd_template


def _resolve_usb_cmd_template(
    apio_ctx: ApioContext, scanner: _DeviceScanner, cmd_template: str
) -> str:
    """Resolves a programmer command template for an USB device."""

    # -- Match to a single usb device.
    device: UsbDevice = _match_usb_device(apio_ctx, scanner)

    # -- Substitute vars.
    cmd_template = cmd_template.replace(VID_VAR, device.vendor_id)
    cmd_template = cmd_template.replace(PID_VAR, device.product_id)
    cmd_template = cmd_template.replace(BUS_VAR, str(device.bus))
    cmd_template = cmd_template.replace(DEV_VAR, str(device.device))
    cmd_template = cmd_template.replace(SERIAL_NUM_VAR, device.serial_number)

    # -- Sanity check, should have no usb vars unresolved.
    # assert not any(s in cmd_template for s in USB_VARS), cmd_template

    # -- All done.
    return cmd_template


def _construct_cmd_template(apio_ctx: ApioContext) -> str:
    """Construct a command template for the board. This is

    Example of output strings:
    "'tinyprog --pyserial -c ${SERIAL_PORT} --program $SOURCE'"
    "'iceprog -d i:0x${VID}:0x${PID} $SOURCE'"
    """

    board = apio_ctx.project["board"]
    board_info = apio_ctx.boards[board]

    # -- Get the programmer type
    # -- Ex. type: "tinyprog"
    # -- Ex. type: "iceprog"
    prog_info = board_info["programmer"]
    prog_type = prog_info["type"]

    # -- Get all the information for that type of programmer
    # -- * command
    # -- * arguments
    # -- * pip package
    programmer_info = apio_ctx.programmers[prog_type]

    # -- Get the command (without arguments) to execute
    # -- for programming the current board
    # -- Ex. "tinyprog"
    # -- Ex. "iceprog"
    cmd_template = programmer_info["command"]

    # -- Let's add the arguments for executing the programmer
    if programmer_info.get("args"):
        cmd_template += f" {programmer_info['args']}"

    # -- Mark the expected location of the bitstream file name, before
    # -- we append any arg to the command. Some programmers such as
    # -- dfu-util require it immediatly after the "args" string.
    cmd_template += " $SOURCE"

    # -- Some tools need extra arguments
    # -- (like dfu-util for example)
    if prog_info.get("extra_args"):
        cmd_template += f" {prog_info['extra_args']}"

    return cmd_template


def _match_serial_device(
    apio_ctx: ApioContext,
    scanner: _DeviceScanner,
    ext_serial_port: Optional[str],
) -> SerialDevice:
    """Scans the serial devices and selects and returns a single matching
    device. Exits with an error if none or multiple matching devices.
    """

    # -- Get board info.
    board = apio_ctx.project["board"]
    board_info = apio_ctx.boards[board]

    # -- Scan for all serial devices.
    all_devices: List[SerialDevice] = scanner.get_serial_devices()

    # -- Get board optional usb constraints
    usb_info = board_info.get("usb", {})
    # vid = usb_info.get("vid", None)
    # pid = usb_info.get("pid", None)
    # desc_regex = usb_info.get("desc-regex", )

    # -- Construct a device filter.
    filt = SerialDeviceFilter()
    if "vid" in usb_info:
        filt.vendor_id(usb_info["vid"])
    if "pid" in usb_info:
        filt.product_id(usb_info["pid"])
    if "desc-regex" in usb_info:
        filt.desc_regex(usb_info["desc-regex"])
    if ext_serial_port:
        filt.port(ext_serial_port)

    # -- Get matching devices
    matching: List[SerialDevice] = filt.filter(all_devices)

    if util.is_debug():
        cout(f"Serial device filter: {str(filt)}")
        cout(f"Matching serial devices: {matching}")

    if util.is_debug():
        cout(f"Matching serial devices: {matching}")

    # -- Error if not exactly one match.
    if not matching:
        cerror(f"Serial board '{board}' not found.")
        cout(
            "Type 'apio devices serial' to list the serial devices.",
            f"Filter used: {str(filt)}",
            style=INFO,
        )

    # -- Error more than one match
    if len(matching) > 1:
        cerror(
            f"Found {len(matching)} serial devices "
            f"matching'{board}' board."
        )
        cout(
            "Type 'apio devices serial' to list the serial devices.",
            f"Filter used: {str(filt)}",
            style=INFO,
        )

    if util.is_debug():
        cout(f"Serial device: {matching[0]}")

    # -- All done. We have a single match.
    return matching[0]


def _match_usb_device(apio_ctx: ApioContext, scanner) -> UsbDevice:
    """Scans the USB devices and selects and returns a single matching
    device. Exits with an error if none or multiple matching devices.
    """

    # -- Get the board info.
    board = apio_ctx.project["board"]
    board_info = apio_ctx.boards[board]

    # -- Scan for all serial devices.
    all_devices: List[UsbDevice] = scanner.get_usb_devices()

    # -- Get board optional usb constraints
    usb_info = board_info.get("usb", {})

    # -- Construct a device filter.
    filt = UsbDeviceFilter()
    if "vid" in usb_info:
        filt.vendor_id(usb_info["vid"])
    if "pid" in usb_info:
        filt.product_id(usb_info["pid"])
    if "desc-regex" in usb_info:
        filt.desc_regex(usb_info["desc-regex"])

    # -- Get matching devices
    matching: List[UsbDevice] = filt.filter(all_devices)

    if util.is_debug():
        cout(f"USB device filter: {str(filt)}")
        cout(f"Matching USB devices: {matching}")

    if util.is_debug():
        cout(f"Matching usb devices: {matching}")

    # -- Error if not exactly one match.
    if not matching:
        cerror(f"USB board '{board}' not found.")
        cout(
            "Type 'apio devices usb' to list the usb devices.",
            f"Filter used: {str(filt)}",
            style=INFO,
        )
        sys.exit(1)

    # -- Error more than one match
    if len(matching) > 1:
        cerror(
            f"Found {len(matching)} usb devices " f"matching'{board}' board."
        )
        cout(
            "Type 'apio devices usb' for the list of available devices.",
            f"Filter used: {str(filt)}",
            style=INFO,
        )
        sys.exit(1)

    if util.is_debug():
        cout(f"USB device: {matching[0]}")

    # -- All done. We have a single match.
    return matching[0]
