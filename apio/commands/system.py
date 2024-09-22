# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO SYSTEM command"""

from pathlib import Path
import inspect
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
    help="Show platform id and other info.",
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

    # -- Verify exlusive flags.
    flags_count = int(lsftdi) + int(lsusb) + int(lsserial) + int(info)
    if flags_count > 1:
        click.secho(
            (
                "Error: --lsftdi, --lsusb, --lsserial, and --info"
                " are mutually exclusive."
            ),
            fg="red",
        )
        ctx.exit(1)

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
        click.secho(get_systype(), fg="yellow")

        # -- Print apio package source directory.
        this_file_path = inspect.getfile(lambda: None)
        apio_source_path = Path(this_file_path).parent.parent
        click.secho("Source:   ", nl=False)
        click.secho(apio_source_path, fg="yellow")
        ctx.exit(0)

    # -- Invalid option. Just show the help
    click.secho(ctx.get_help())
    ctx.exit(0)
