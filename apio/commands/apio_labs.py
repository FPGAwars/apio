# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio api' command"""

import sys
from typing import Optional, List
from dataclasses import dataclass
from glob import glob
import click
from rich.table import Table
from rich import box
import usb.core
import usb.backend.libusb1
from apio.managers import installer
from apio.commands import options
from apio.common.apio_console import cout, cprint, cerror
from apio.common.apio_styles import ERROR, BORDER, EMPH3, SUCCESS, INFO
from apio.utils import util
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand

# -- Mapping of FTDI PID to IC model number. Try to keep it consistent with
# -- src/libusb_ll.cpp#L159 at https://github.com/trabucayre/openFPGALoader.
FTDI_PID_TO_MODEL = {
    0x6001: "FT232R",  # Most common UART interface
    0x6010: "FT2232H",  # Dual channel, high-speed
    0x6011: "FT4232H",  # Quad channel, high-speed
    0x6014: "FT232H",  # Single channel, high-speed, multi-protocol
    0x6015: "FTX Series",  # Includes FT231X, FT234X (basic UART)
    0x6017: "FT313H",  # USB host controller IC
    0x8372: "FT245R",  # Parallel FIFO interface
    0x8371: "FT232BM",  # Older UART chip
    0x8373: "FT2232C",  # Early dual interface device
    0x8374: "FT4232",  # Early quad interface device
}

# ------ apio labs scan-usb


@dataclass()
class UsbDevice:
    """A data class to hold the information of a single USB device."""

    # pylint: disable=too-many-instance-attributes

    bus: int
    device: int
    vendor_id: str
    product_id: str
    manufacturer: str
    description: str
    serial_num: str
    device_type: str


def get_usb_str(
    device: usb.core.Device, index: int, default: str, verbose: bool
) -> Optional[str]:
    """Extract usb string by its index."""
    # pylint: disable=broad-exception-caught
    try:
        s = usb.util.get_string(device, index)
        # For Tang 9K which contains a null char as a string separator.
        # It's not USB standard but C tools do that implicitly.
        s = s.split("\x00", 1)[0]
        return s
    except Exception as e:
        if verbose:
            print(f"Error getting USB string at index {index}: {e}")
        return default


def get_usb_devices(apio_ctx: ApioContext, verbose: bool) -> List[UsbDevice]:
    """Query and return a list with usb device info."""

    # -- Track the names we searched for. For diagnostics.
    searched_names = []

    def find_library(name: str):
        """A callback for looking up the libusb backend file."""

        cout("find_library() call:")
        cout(f"   {name=}")

        # -- Track searched names, for diagnostics
        searched_names.append(name)

        # -- Try to match to a lib in oss-cad-suite/lib.
        oss_dir = apio_ctx.get_package_dir("oss-cad-suite")
        pattern = oss_dir / "lib" / f"lib{name}*"
        files = glob(str(pattern))

        cout(f"   {pattern=}")
        cout(f"   {files=}")

        # -- We don't expect multiple matches.
        if len(files) > 1:
            cerror(f"Found multiple backends for '{name}': {files}")
            sys.exit(1)

        if files:
            return files[0]
        return None

    # -- Lookup libusb backend library file in oss-cad-suite/lib.
    backend = usb.backend.libusb1.get_backend(find_library=find_library)

    if not backend:
        cerror("Libusb backend not found")
        cout(f"Searched names: {searched_names}", style=INFO)
        sys.exit(1)

    # -- Find the usb devices.
    devices: List[usb.core.Device] = usb.core.find(
        find_all=True, backend=backend
    )

    # -- Collect the devices
    result: List[UsbDevice] = []
    for device in devices:
        # -- Print entire device info for debugging.
        if verbose:
            cout()
            cout(str(device))
            cout()

        # -- Sanity check.
        assert isinstance(device, usb.core.Device), type(device)

        # -- Skip hubs, they are not interesting.
        if device.bDeviceClass == 0x09:
            continue

        # -- Determine ftdi type.

        if device.idVendor == 0x0403:
            # -- This is an FTDI device, so look up its type by its PID.
            device_type = FTDI_PID_TO_MODEL.get(device.idProduct, "FTDI")
        else:
            # -- Not an FTDI device, so no type.
            device_type = ""

        # -- Create the device object.
        item = UsbDevice(
            bus=device.bus,
            device=device.address,
            vendor_id=device.idVendor,
            product_id=device.idProduct,
            manufacturer=get_usb_str(
                device,
                device.iManufacturer,
                default="(unavail)",
                verbose=verbose,
            ),
            description=get_usb_str(
                device, device.iProduct, default="(unavail)", verbose=verbose
            ),
            serial_num=get_usb_str(
                device, device.iSerialNumber, default="", verbose=verbose
            ),
            device_type=device_type,
        )
        result.append(item)

    # -- Sort by (bus, device).
    result = sorted(result, key=lambda d: (d.bus, d.device))

    # -- All done.
    return result


# -- Text in the rich-text format of the python rich library.
APIO_API_LABS_SCAN_USB_HELP = """
The command 'apio labs scan-usb' is a temporary command that is used \
to evaluate a new way to scan USB devices connected to the host \
system. It is not part of the official apio command set and \
most likely will change or be removed in the future.

Examples:[code]
  apio labs scan-usb     # Scan and print USB devices
  apio labs scan-usb -v  # With extra info[/code]
"""


@click.command(
    name="scan-usb",
    cls=ApioCommand,
    short_help="An experimental command to scan USB devices.",
    help=APIO_API_LABS_SCAN_USB_HELP,
)
@options.verbose_option
def _scan_usb_cli(
    # -- Options
    verbose: bool,
):
    """Implements the 'apio labs scan-usb' command."""

    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- Prepare the packages for use.
    installer.install_missing_packages_on_the_fly(apio_ctx)

    # -- Get the list of devices
    devices = get_usb_devices(apio_ctx, verbose=verbose)

    # -- If not found, print a message and exit.
    if not devices:
        cout("No USB devices found.", style=ERROR)
        return

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style=BORDER,
        title="USB Devices",
        title_justify="left",
    )

    # -- Add columns
    table.add_column("BUS:DEV", no_wrap=True, justify="center")
    # table.add_column("DEV", no_wrap=True, justify="center")
    table.add_column("VID:PID", no_wrap=True)
    # table.add_column("PID", no_wrap=True)
    table.add_column("MANUFACTURER", no_wrap=True, style=EMPH3)
    table.add_column("DESCRIPTION", no_wrap=True, style=EMPH3)
    table.add_column("SERIAL-NUM", no_wrap=True)
    table.add_column("TYPE", no_wrap=True)

    # -- Add a raw per device
    for device in devices:
        values = []
        values.append(f"{device.bus}:{device.device}")
        values.append(f"{device.vendor_id:04X}:{device.product_id:04X}")
        values.append(device.manufacturer)
        values.append(device.description)
        values.append(device.serial_num)
        values.append(device.device_type)

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    cprint(table)
    cout(f"Found {util.plurality(devices, 'USB device')}", style=SUCCESS)


# ------ apio apio

# -- Text in the rich-text format of the python rich library.
APIO_API_HELP = """
The command group 'apio labs' contains experimental commands that are used \
to evaluate new features and ideas. They are not part of the official apio \
command set and most likely change or be removed in the future.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _scan_usb_cli,
            # _ftdi_scan_cli,
        ],
    )
]


@click.command(
    name="labs",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Experimental apio commands.",
    help=APIO_API_HELP,
)
def cli():
    """Implements the 'apio labs' command group."""

    # pass
