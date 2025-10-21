# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio devices' command"""

import sys
import click
from rich.table import Table
from rich import box
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand
from apio.common.apio_console import cout, ctable
from apio.common.apio_styles import BORDER, SUCCESS, ERROR, EMPH3
from apio.utils import serial_util, usb_util, util


# --- apio devices usb


def _list_usb_devices(apio_ctx: ApioContext) -> None:
    """Lists the connected USB devices in table format."""

    devices = usb_util.scan_usb_devices(apio_ctx=apio_ctx)

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
    table.add_column("VID:PID", no_wrap=True)
    table.add_column("BUS:DEV", no_wrap=True, justify="center")
    table.add_column("MANUFACTURER", no_wrap=True, style=EMPH3)
    table.add_column("PRODUCT", no_wrap=True, style=EMPH3)
    table.add_column("SERIAL-NUM", no_wrap=True)
    table.add_column("TYPE", no_wrap=True)

    # -- Add a raw per device
    for device in devices:
        values = []
        values.append(f"{device.vendor_id}:{device.product_id}")
        values.append(f"{device.bus}:{device.device}")
        values.append(device.manufacturer)
        values.append(device.product)
        values.append(device.serial_number)
        values.append(device.device_type)

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    ctable(table)
    cout(f"Found {util.plurality(devices, 'USB device')}", style=SUCCESS)


# -- Text in the rich-text format of the python rich library.
APIO_DEVICES_USB_HELP = """
The command 'apio devices usb' displays the USB devices currently \
connected to your computer. It is useful for diagnosing FPGA board \
connectivity issues.

Examples:[code]
  apio devices usb    # List the usb devices.[/code]

"""


@click.command(
    name="usb",
    cls=ApioCommand,
    short_help="List USB devices.",
    help=APIO_DEVICES_USB_HELP,
)
def _usb_cli():
    """Implements the 'apio devices usb' command."""

    # Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- List all usb devices
    _list_usb_devices(apio_ctx)
    sys.exit(0)


# -- apio devices serial


def _list_serial_devices() -> None:
    """Lists the connected serial devices in table format."""

    devices = serial_util.scan_serial_devices()

    # -- If not found, print a message and exit.
    if not devices:
        cout("No SERIAL devices found.", style=ERROR)
        return

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style=BORDER,
        title="SERIAL Ports",
        title_justify="left",
    )

    # -- Add columns
    table.add_column("PORT", no_wrap=True, style=EMPH3)
    table.add_column("VID:PID", no_wrap=True)
    table.add_column("MANUFACTURER", no_wrap=True, style=EMPH3)
    table.add_column("PRODUCT", no_wrap=True, style=EMPH3)
    table.add_column("SERIAL-NUM", no_wrap=True)
    table.add_column("TYPE", no_wrap=True)

    # -- Add a raw per device
    for device in devices:
        values = []
        values.append(device.port)
        values.append(f"{device.vendor_id}:{device.product_id}")
        values.append(device.manufacturer)
        values.append(device.product)
        values.append(device.serial_number)
        values.append(device.device_type)

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    ctable(table)
    cout(f"Found {util.plurality(devices, 'device')}", style=SUCCESS)


# -- Text in the rich-text format of the python rich library.
APIO_DEVICES_SERIAL_HELP = """
The command 'apio devices serial' displays the serial devices currently \
connected to your computer. It is useful for diagnosing FPGA board \
connectivity issues.

Examples:[code]
  apio devices serial    # List the serial devices.[/code]

Note that devices such as FTDI FTDI2232 that have more than one channel \
are listed as multiple rows, one for each of their serial ports.

On Windows, manufacturer and product strings of FTDI based devices \
may show their FTDI generic values rather than the custom values such \
such as 'Alhambra II' set by the device manufacturer.
"""


@click.command(
    name="serial",
    cls=ApioCommand,
    short_help="List serial devices.",
    help=APIO_DEVICES_SERIAL_HELP,
)
def _serial_cli():
    """Implements the 'apio devices serial' command."""

    # -- Create the apio context. We create it for consistency though
    # -- we don't use .t
    _ = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- List all connected serial devices
    _list_serial_devices()
    sys.exit(0)


# --- apio devices

# -- Text in the rich-text format of the python rich library.
APIO_DEVICES_HELP = """
The command group 'apio devices' includes subcommands that lists devices
that are attached to the computer. It's main usage is diagnostics or
devices connectivity and drivers.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _usb_cli,
            _serial_cli,
        ],
    )
]


@click.command(
    name="devices",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="List attached devices.",
    help=APIO_DEVICES_HELP,
)
def cli():
    """Implements the 'apio devices' command."""

    # pass
