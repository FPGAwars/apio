# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio labs' command"""

import click
from rich.table import Table
from rich import box
from apio.managers import installer
from apio.commands import options
from apio.common.apio_console import cout, cprint
from apio.common.apio_styles import ERROR, BORDER, EMPH3, SUCCESS
from apio.utils import util, usb_util
from apio.apio_context import ApioContext, ApioContextScope
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand


# ------ apio labs scan-usb


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
    devices = usb_util.scan_usb_devices(apio_ctx, verbose=verbose)

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
    table.add_column("DESCRIPTION", no_wrap=True, style=EMPH3)
    table.add_column("SERIAL-NUM", no_wrap=True)
    table.add_column("TYPE", no_wrap=True)

    # -- Add a raw per device
    for device in devices:
        values = []
        values.append(f"{device.vendor_id:04X}:{device.product_id:04X}")
        values.append(f"{device.bus}:{device.device}")
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
