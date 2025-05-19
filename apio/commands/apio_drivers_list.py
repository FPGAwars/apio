# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio drivers list' command"""

import sys
import click
from rich.table import Table
from rich import box
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand
from apio.managers import installer
from apio.common.apio_console import cout, cprint
from apio.common.apio_styles import BORDER, SUCCESS, ERROR, EMPH3
from apio.utils import pkg_util, ftdi_util, usb_util, serial_util, util


# -- apio drivers list ftdi


def _list_ftdi_devices(apio_ctx: ApioContext) -> None:
    """Lists the connected FTDI devices in table format."""

    installer.install_missing_packages_on_the_fly(apio_ctx)
    pkg_util.set_env_for_packages(apio_ctx, quiet=True)

    devices = ftdi_util.scan_ftdi_devices()

    # -- If not found, print a message and exit.
    if not devices:
        cout("No FTDI devices found.", style=ERROR)
        return

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style=BORDER,
        title="FTDI Devices",
        title_justify="left",
    )

    # -- Add columns
    table.add_column("TYPE", no_wrap=True)
    table.add_column("MANUFACTURER", no_wrap=True, style=EMPH3)
    table.add_column("DESCRIPTION", no_wrap=True, style=EMPH3)
    table.add_column("VID", no_wrap=True)
    table.add_column("PID", no_wrap=True)
    table.add_column("SERIAL-NUM", no_wrap=True)
    table.add_column("BUS", no_wrap=True, justify="center")
    table.add_column("DEVICE", no_wrap=True, justify="center")

    # -- Add a raw per device
    for device in devices:
        values = []
        values.append(device.type)
        values.append(device.manufacturer)
        values.append(device.description)
        values.append(device.vendor_id)
        values.append(device.product_id)
        values.append(device.serial_number)
        values.append(str(device.bus))
        values.append(str(device.device))

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    cprint(table)
    cout(f"Found {util.plurality(devices, 'device')}", style=SUCCESS)


# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_LIST_FTDI_HELP = """
The command 'apio drivers list ftdi' displays the FTDI devices currently \
connected to your computer. It is useful for diagnosing FPGA board \
connectivity issues.

Examples:[code]
  apio drivers list ftdi    # List the ftdi devices.[/code]

[Note] When apio is installed on Linux using the Snap package \
manager, run the command 'snap connect apio:raw-usb' once \
to grant the necessary permissions to access USB devices.

[Hint] This command invokes the command below and displays its output in a \
table form:

[code]  apio raw -- openFPGALoader --scan-usb[code]
"""


@click.command(
    name="ftdi",
    cls=ApioCommand,
    short_help="List the connected ftdi devices.",
    help=APIO_DRIVERS_LIST_FTDI_HELP,
)
def _ftdi_cli():
    """Implements the 'apio drivers list ftdi' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- List all connected ftdi devices
    _list_ftdi_devices(apio_ctx)
    sys.exit(0)


# -- apio drivers list serial


def _list_serial_devices(apio_ctx: ApioContext) -> None:
    """Lists the connected serial devices in table format."""

    installer.install_missing_packages_on_the_fly(apio_ctx)
    pkg_util.set_env_for_packages(apio_ctx, quiet=True)

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
        title="SERIAL Devices",
        title_justify="left",
    )

    # -- Add columns
    table.add_column("MANUFACTURER", no_wrap=True, style=EMPH3)
    table.add_column("DESCRIPTION", no_wrap=True, style=EMPH3)
    table.add_column("VID", no_wrap=True)
    table.add_column("PID", no_wrap=True)
    table.add_column("SERIAL-NUM", no_wrap=True)
    table.add_column("PORT", no_wrap=True)

    # -- Add a raw per device
    for device in devices:
        values = []
        values.append(device.manufacturer)
        values.append(device.description)
        values.append(device.vendor_id)
        values.append(device.product_id)
        values.append(device.serial_number)
        values.append(device.port)

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    cprint(table)
    cout(f"Found {util.plurality(devices, 'device')}", style=SUCCESS)


# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_LIST_SERIAL_HELP = """
The command 'apio drivers list serial' displays the serial devices currently \
connected to your computer. It is useful for diagnosing FPGA board \
connectivity issues.

Examples:[code]
  apio drivers list serial    # List the serial devices.[/code]

Note that devices such as FTDI FTDI2232 that have more than one channel \
are listed as multiple rows, one for each of their serial ports.
"""


@click.command(
    name="serial",
    cls=ApioCommand,
    short_help="List the connected serial devices.",
    help=APIO_DRIVERS_LIST_SERIAL_HELP,
)
def _serial_cli():
    """Implements the 'apio drivers list serial' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- List all connected serial devices
    _list_serial_devices(apio_ctx)
    sys.exit(0)


# --- apio drivers list usb


def _list_usb_devices(apio_ctx: ApioContext) -> None:
    """Lists the connected USB devices in table format."""

    installer.install_missing_packages_on_the_fly(apio_ctx)
    pkg_util.set_env_for_packages(apio_ctx, quiet=True)

    devices = usb_util.scan_usb_devices()

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
    table.add_column("VID", no_wrap=True, style=EMPH3)
    table.add_column("PID", no_wrap=True, style=EMPH3)
    table.add_column("BUS", no_wrap=True, justify="center")
    table.add_column("DEVICE", no_wrap=True, justify="center")
    table.add_column("PATH", no_wrap=True, justify="center")

    # -- Add a raw per device
    for device in devices:
        values = []
        values.append(device.vendor_id)
        values.append(device.product_id)
        values.append(str(device.bus))
        values.append(str(device.device))
        values.append(str(device.path))

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    cprint(table)
    cout(f"Found {util.plurality(devices, 'USB device')}", style=SUCCESS)


# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_LIST_USB_HELP = """
The command 'apio drivers list usb' displays the USB devices currently \
connected to your computer. It is useful for diagnosing FPGA board \
connectivity issues.

Examples:[code]
  apio drivers list usb    # List the usb devices.[/code]

[Note] When apio is installed on Linux using the Snap package \
manager, run the command 'snap connect apio:raw-usb' once \
to grant the necessary permissions to access USB devices.

[Hint] This command invokes the command below and displays its output in a \
table form:

[code]  apio raw -- lsusb[code]
"""


@click.command(
    name="usb",
    cls=ApioCommand,
    short_help="List connected USB devices.",
    help=APIO_DRIVERS_LIST_USB_HELP,
)
def _usb_cli():
    """Implements the 'apio drivers list usb' command."""

    # Create the apio context.
    apio_ctx = ApioContext(scope=ApioContextScope.NO_PROJECT)

    # -- List all connected usb devices
    _list_usb_devices(apio_ctx)
    sys.exit(0)


# --- apio drivers list

# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_LIST_HELP = """
The command group 'apio drivers list' includes subcommands that that lists \
system drivers that are used with FPGA boards.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _ftdi_cli,
            _serial_cli,
            _usb_cli,
        ],
    )
]


@click.command(
    name="list",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="List system drivers.",
    help=APIO_DRIVERS_LIST_HELP,
)
def cli():
    """Implements the 'apio drivers list' command."""

    # pass
