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
from apio.managers.system import System
from apio.managers import installer
from apio.common.apio_console import cout, cprint
from apio.common.apio_styles import BORDER, SUCCESS, ERROR, EMPH3
from apio.utils import pkg_util, ftdi_util, util


# -- apio drivers list ftdi


def _list_ftdi_devices(apio_ctx: ApioContext) -> None:
    """Lists the connected FTDI devices in table format."""

    installer.install_missing_packages_on_the_fly(apio_ctx)
    pkg_util.set_env_for_packages(apio_ctx, quiet=True)

    devices = ftdi_util.get_devices()

    # -- If not found, print a message and exit.
    if not devices:
        cout("No devices found.", style=ERROR)
        return

    # -- Define the table.
    table = Table(
        show_header=True,
        show_lines=True,
        box=box.SQUARE,
        border_style=BORDER,
    )

    # -- Add columns
    table.add_column("INDEX", no_wrap=True, justify="center")
    table.add_column("TYPE", no_wrap=True)
    table.add_column("MANUFACTURER", no_wrap=True, style=EMPH3)
    table.add_column("DESCRIPTION", no_wrap=True, style=EMPH3)
    table.add_column("VID", no_wrap=True)
    table.add_column("PID", no_wrap=True)
    table.add_column("SERIAL", no_wrap=True)
    table.add_column("BUS", no_wrap=True, justify="center")
    table.add_column("DEVICE", no_wrap=True, justify="center")

    # -- Add a raw per device
    for device in devices:
        values = []
        values.append(str(device.index))
        values.append(device.type)
        values.append(device.manufacturer)
        values.append(device.description)
        values.append(device.vendor_id)
        values.append(device.product_id)
        values.append(device.serial_code)
        values.append(str(device.bus))
        values.append(str(device.device))

        # -- Add row.
        table.add_row(*values)

    # -- Render the table.
    cout()
    cprint(table)
    cout(f"Found {util.plurality(devices, "device")}", style=SUCCESS)


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

[code]  'apio raw -- openFPGALoader --scan-usb[code]
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

# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_LIST_SERIAL_HELP = """
The command 'apio drivers list serial' lists the serial devices connected to \
your computer. It is useful for diagnosing FPGA board connectivity issues.

Examples:[code]
  apio drivers list serial   # List the serial devices.[/code]

[b][Hint][/b] This command executes the utility lsserial, which can also be \
invoked using the command 'apio raw -- lsserial ...'.
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

    # -- Create the system object
    system = System(apio_ctx)

    # # -- List all connected serial devices
    exit_code = system.lsserial()
    sys.exit(exit_code)


# --- apio drivers list usb

# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_LIST_USB_HELP = """
The command 'apio drivers list usb' runs the lsusb utility to list the USB \
devices connected to your computer. It is typically used for diagnosing  \
connectivity issues with FPGA boards.

Examples:[code]
  apio drivers list usb    # List the usb devices[/code]

[b][Hint][/b] You can also run the lsusb utility using the command \
'apio raw -- lsusb ...'.
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

    # -- Create the system object
    system = System(apio_ctx)

    # -- List the USB device.
    exit_code = system.lsusb()
    sys.exit(exit_code)


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
