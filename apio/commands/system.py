# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio system' command"""

from pathlib import Path
from varname import nameof
import click
from click.core import Context
from apio import util
from apio import cmd_util
from apio.util import get_system_type
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
    cls=cmd_util.ApioOption,
)

lsusb_option = click.option(
    "lsusb",  # Var name.
    "--lsusb",
    is_flag=True,
    help="List all connected USB devices.",
    cls=cmd_util.ApioOption,
)

lsserial_option = click.option(
    "lsserial",  # App name.
    "--lsserial",
    is_flag=True,
    help="List all connected Serial devices.",
    cls=cmd_util.ApioOption,
)

info_option = click.option(
    "info",  # Var name.
    "-i",
    "--info",
    is_flag=True,
    help="Show platform id and other info.",
    cls=cmd_util.ApioOption,
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

The flags --lstdi, --lsusb, --lsserial, and --info are exclusive and
cannot be mixed in the same command.
"""


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    "system",
    short_help="Provides system info.",
    help=HELP,
    cls=cmd_util.ApioCommand,
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

    # Make sure these params are exclusive.
    cmd_util.check_exclusive_params(ctx, nameof(lsftdi, lsusb, lsserial, info))

    # Load the various resource files.
    resources = Resources(project_dir=project_dir, project_scope=False)

    # -- Create the system object
    system = System(resources)

    # -- List all connected ftdi devices
    if lsftdi:
        exit_code = system.lsftdi()
        ctx.exit(exit_code)

    # -- List all connected USB devices
    if lsusb:
        exit_code = system.lsusb()
        ctx.exit(exit_code)

    # -- List all connected serial devices
    if lsserial:
        exit_code = system.lsserial()
        ctx.exit(exit_code)

    # -- Show system information
    if info:
        # -- Print platform id.
        click.secho("Platform: ", nl=False)
        click.secho(get_system_type(), fg="yellow")

        # -- Print apio package directory.
        click.secho("Package:  ", nl=False)
        click.secho(util.get_path_in_apio_package(""), fg="yellow")

        # -- Print apio home directory.
        click.secho("Home:     ", nl=False)
        click.secho(util.get_home_dir(), fg="yellow")

        ctx.exit(0)

    # -- Invalid option. Just show the help
    click.secho(ctx.get_help())
