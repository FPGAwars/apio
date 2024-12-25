# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio system' command"""

import sys
import importlib.metadata
import click
from apio import util
from apio.managers.system import System
from apio.apio_context import ApioContext
from apio.cmd_util import ApioGroup, ApioSubgroup


# ------ apio system lsftdi

LSFTDI_HELP = """
The 'apio system lsftdi' commands runs the lsftdi utility to list ftdi
devices connector to your computer and is useful for diagnosing connectivity
issues with FPGA boards.

\b
Examples:
  apio system  lsftdi      # List FTDI devices

[Hint] Another way to run the lsftd utility is using the command
'apio raw -- lsftdi <flags>'
"""


@click.command(
    name="lsftdi",
    short_help="List connected FTDI devices.",
    help=LSFTDI_HELP,
)
def _lsftdi_cli():
    """Implements the 'apio system lsftdi' command."""

    # Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Create the system object
    system = System(apio_ctx)

    # -- List all connected ftdi devices
    exit_code = system.lsftdi()
    sys.exit(exit_code)


# ------ apio system lsusb

LSUSB_HELP = """
The 'apio system lsfusb' commands runs the lsusb utility to list ftdi
devices connector to your computer and is useful for diagnosing connectivity
issues with FPGA boards.

\b
Examples:
  apio system  lsusb      # List USB devices

[Hint] Another way to run the lsusb utility is using the command
'apio raw -- lsusb <flags>'
"""


@click.command(
    name="lsusb",
    short_help="List connected USB devices.",
    help=LSFTDI_HELP,
)
def _lsusb_cli():
    """Implements the 'apio system lsusb' command."""

    # Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Create the system object
    system = System(apio_ctx)

    # -- List the USB device.
    exit_code = system.lsusb()
    sys.exit(exit_code)


# ------ apio system lsserial

LSSERIAL_HELP = """
The system command provides system info that help diagnosing apio
installation and connectivity issue.

\b
Examples:
  apio system lsserial   # List serial devices
"""


@click.command(
    name="lsserial",
    short_help="List connected serial devices.",
    help=LSSERIAL_HELP,
)
def _lsserial_cli():
    """Implements the 'apio system lsserial' command."""

    # Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Create the system object
    system = System(apio_ctx)

    # # -- List all connected serial devices
    exit_code = system.lsserial()
    sys.exit(exit_code)


# ------ apio system info

INFO_HELP = """
The 'apio system info' command provides general informaion about your system
and apio installation and is useful for diagnosing apio installation issues.

\b
Examples:
  apio system info       # Show platform id and info.

[Advanced] The default location of the apio home directory, where preferences
and packages are stored, is in the .apio directory under the user home
directory, but can be changed using the APIO_HOME environment variable.

"""


@click.command(
    name="info",
    short_help="Show platform id and other info.",
    help=LSFTDI_HELP,
)
def _info_cli():
    """Implements the 'apio system info' command."""

    # Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Print apio version.
    click.secho("Apio version    ", nl=False)
    click.secho(importlib.metadata.version("apio"), fg="cyan")

    # -- Print python version.
    click.secho("Python version  ", nl=False)
    click.secho(util.get_python_version(), fg="cyan")

    # -- Print platform id.
    click.secho("Platform id     ", nl=False)
    click.secho(apio_ctx.platform_id, fg="cyan")

    # -- Print apio package directory.
    click.secho("Python package  ", nl=False)
    click.secho(util.get_path_in_apio_package(""), fg="cyan")

    # -- Print apio home directory.
    click.secho("Apio home       ", nl=False)
    click.secho(apio_ctx.home_dir, fg="cyan")

    # -- Print apio home directory.
    click.secho("Apio packages   ", nl=False)
    click.secho(apio_ctx.packages_dir, fg="cyan")


# ------ apio system platforms

PLATFORMS_HELP = """
The 'apio system platforms' command lists the platforms ids supported by
apio, with the effective platform id of your system highlightd.

\b
Examples:
  apio system platforms   # List supported platform ids.

[Advanced] The automatic platform id detection of apio can be overriden
by defining a different platform id using the env variable APIO_PLATFORM.
"""


@click.command(
    name="platforms",
    short_help="List supported platforms ids.",
    help=LSFTDI_HELP,
)
def _platforms_cli():
    """Implements the 'apio system platforms' command."""

    # Create the apio context.
    apio_ctx = ApioContext(load_project=False)

    # -- Print title line
    click.secho(
        f"  {'[PLATFORM ID]':18} " f"{'[DESCRIPTION]'}",
        fg="magenta",
    )

    # -- Print a line for each platform id.
    for platform_id, platform_info in apio_ctx.platforms.items():
        # -- Get next platform's info.
        description = platform_info.get("description")
        # -- Determine if it's the current platform id.
        fg = "green" if platform_id == apio_ctx.platform_id else None
        # -- Print the line.
        click.secho(f"  {platform_id:18} {description}", fg=fg)


# ------ apio system

HELP = """
The 'apio system' command group provides various commands that provides
information about the system, including devices and python and apio
installation.

The subcommands of this group are listed below.
"""

# -- We have only a single group with the title 'Subcommands'.
SUBGROUPS = [
    ApioSubgroup(
        "Subcommands",
        [
            _lsftdi_cli,
            _lsusb_cli,
            _lsserial_cli,
            _platforms_cli,
            _info_cli,
        ],
    )
]


@click.command(
    name="system",
    cls=ApioGroup,
    subgroups=SUBGROUPS,
    short_help="Provides system info.",
    help=HELP,
)
def cli():
    """Implements the 'apio system' command group."""

    # pass
