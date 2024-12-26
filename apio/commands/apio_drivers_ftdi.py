# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio drivers ftdi' command"""

import sys
import click
from apio.managers.drivers import Drivers
from apio.apio_context import ApioContext
from apio.cmd_util import ApioGroup, ApioSubgroup
from apio.managers.system import System


# -- apio drivers ftdi install

INSTALL_HELP = """
The command 'apio drivers ftdi install' installs the ftdi drivers on your
system as required by some FPGA boards.

\b
Examples:
  apio drivers fdri install      # Install the ftdi drivers.
  apio drivers fdri uinstall     # Uinstall the ftdi drivers.
"""


@click.command(
    name="install",
    short_help="Install the ftdi drivers.",
    help=INSTALL_HELP,
)
def _install_cli():
    """Implements the 'apio drivers ftdi install' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # # -- FTDI install option
    # if ftdi_install:
    exit_code = drivers.ftdi_install()
    sys.exit(exit_code)


# -- apio driver ftdi uninstall

UNINSTALL_HELP = """
The command 'apio drivers ftdi uninstall' uninstalled the ftdi drivers that
you may installed eariler. .

\b
Examples:
  apio drivers ftdi install      # Install the ftdi drivers.
  apio drivers ftdi uinstall     # Uinstall the ftdi drivers.

"""


@click.command(
    name="uninstall",
    short_help="Uninstall the ftdi drivers.",
    help=UNINSTALL_HELP,
)
def _uninstall_cli():
    """Implements the 'apio drivers ftdi uninstall' command."""

    # -- Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Create the drivers manager.
    drivers = Drivers(apio_ctx)

    # -- Uninstall
    exit_code = drivers.ftdi_uninstall()
    sys.exit(exit_code)


# -- apio drivers ftdi list


LIST_HELP = """
The command 'apio drivers ftdi list' lists the ftdi devices connected
to your computer. It is useful for diagnosing FPGA board connectivity issues.

\b
Examples:
  apio drivers ftdi list     # List the ftdi devices.

[Hint] This command executes the utility `lsftdi` which can also be invoked
using the command `apio raw -- lsftdi <flags>`
"""


@click.command(
    name="list",
    short_help="List the connected ftdi devices.",
    help=LIST_HELP,
)
def _list_cli():
    """Implements the 'apio drivers ftdi list' command."""

    # Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Create the system object
    system = System(apio_ctx)

    # -- List all connected ftdi devices
    exit_code = system.lsftdi()
    sys.exit(exit_code)


# --- apio drivers ftdi

FTDI_HELP = """
The 'apio drivers ftdi' commands group contains subcommands that are used
to manage the ftdi drivers on your system.

The subcommands are listed below.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _install_cli,
            _uninstall_cli,
            _list_cli,
        ],
    )
]


@click.command(
    name="ftdi",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Manage the ftdi drivers.",
    help=FTDI_HELP,
)
def cli():
    """Implements the 'apio drivers ftdi' command."""

    # pass
