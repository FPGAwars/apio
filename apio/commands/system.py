# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO SYSTEM command"""

from pathlib import Path
import click
from click.core import Context
from apio import util
from apio.util import get_systype
from apio.managers.system import System
from apio.resources import Resources
from apio.commands import options

# ---------------------------
# -- COMMAND SPECIFIC OPTIONS
# ---------------------------
lsftdi_option = click.option(
    "lsftdi",  # Var name.
    "--lsftdi",
    is_flag=True,
    help="List all connected FTDI devices.",
)

lsusb_option = click.option(
    "lsusb",  # Var name.
    "--lsusb",
    is_flag=True,
    help="List all connected USB devices.",
)

lsserial_option = click.option(
    "lsserial",  # App name.
    "--lsserial",
    is_flag=True,
    help="List all connected Serial devices.",
)

info_option = click.option(
    "info",  # Var name.
    "-i",
    "--info",
    is_flag=True,
    help="Show platform id.",
)


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The system command provides system info that help diagnosing apio
installation and connectivity issue.

\b
Examples:
  apio system --lsftdi    # List FTDI devices
  apio system --lsusb     # List USB devices
  apio system --lsserial  # List serial devices
  apio system --info      # Show platform id
"""


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
@click.command(
    "system",
    short_help="Provides system info.",
    help=HELP,
    context_settings=util.context_settings(),
)
@click.pass_context
@options.project_dir_option
@lsftdi_option
@lsusb_option
@lsserial_option
@info_option
def cli(
    ctx: Context,
    # Options
    project_dir: Path,
    lsftdi: bool,
    lsusb: bool,
    lsserial: bool,
    info: bool,
):
    """Implements the system command. This command executes assorted
    system tools"""

    # Load the various resource files.
    resources = Resources(project_dir=project_dir)

    # -- Create the system object
    system = System(resources)

    # -- List all connected ftdi devices
    if lsftdi:
        exit_code = system.lsftdi()

    # -- List all connected USB devices
    elif lsusb:
        exit_code = system.lsusb()

    # -- List all connected serial devices
    elif lsserial:
        exit_code = system.lsserial()

    # -- Show system information
    elif info:
        click.secho("Platform: ", nl=False)
        click.secho(get_systype(), fg="yellow")
        exit_code = 0

    # -- Invalid option. Just show the help
    else:
        click.secho(ctx.get_help())
        exit_code = 0

    # -- Done!
    ctx.exit(exit_code)
