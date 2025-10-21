# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Implementation of 'apio drivers install' command"""

import sys
import click
from apio.managers.drivers import Drivers
from apio.apio_context import (
    ApioContext,
    PackagesPolicy,
    ProjectPolicy,
    RemoteConfigPolicy,
)
from apio.utils.cmd_util import ApioGroup, ApioSubgroup, ApioCommand


# -- apio drivers install ftdi

# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_INSTALL_FTDI_HELP = """
The command 'apio drivers install ftdi' installs on your system the FTDI \
drivers required by some FPGA boards.

Examples:[code]
  apio drivers install ftdi   # Install the ftdi drivers.[/code]
"""


@click.command(
    name="ftdi",
    cls=ApioCommand,
    short_help="Install the ftdi drivers.",
    help=APIO_DRIVERS_INSTALL_FTDI_HELP,
)
def _ftdi_cli():
    """Implements the 'apio drivers install ftdi' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # -- Install.
    exit_code = drivers.ftdi_install()
    sys.exit(exit_code)


# -- apio driver install serial

# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_INSTALL_SERIAL_HELP = """
The command 'apio drivers install serial' installs the necessary serial \
drivers on your system, as required by certain FPGA boards.

Examples:[code]
  apio drivers install serial  # Install the serial drivers.[/code]
"""


@click.command(
    name="serial",
    cls=ApioCommand,
    short_help="Install the serial drivers.",
    help=APIO_DRIVERS_INSTALL_SERIAL_HELP,
)
def _serial_cli():
    """Implements the 'apio drivers install serial' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(
        project_policy=ProjectPolicy.NO_PROJECT,
        remote_config_policy=RemoteConfigPolicy.CACHED_OK,
        packages_policy=PackagesPolicy.ENSURE_PACKAGES,
    )

    # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # Install
    exit_code = drivers.serial_install()
    sys.exit(exit_code)


# --- apio drivers install

# -- Text in the rich-text format of the python rich library.
APIO_DRIVERS_INSTALL_HELP = """
The command group 'apio drivers install' includes subcommands that that \
install system drivers that are used to upload designs to FPGA boards.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _ftdi_cli,
            _serial_cli,
        ],
    )
]


@click.command(
    name="install",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Install drivers.",
    help=APIO_DRIVERS_INSTALL_HELP,
)
def cli():
    """Implements the 'apio drivers install' command."""

    # pass
