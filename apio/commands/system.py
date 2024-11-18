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
from apio import util
from apio import cmd_util
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

platforms_option = click.option(
    "platforms",  # Var name.
    "-p",
    "--platforms",
    is_flag=True,
    help="Show supported platforms ids.",
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
  apio system --lsftdi     # List FTDI devices
  apio system --lsusb      # List USB devices
  apio system --lsserial   # List serial devices
  apio system --info       # Show platform id and info.

The flags --lstdi, --lsusb, --lsserial, and --info are exclusive and
cannot be mixed in the same command.

[Advanced] The system configuration can be overriden using the system env
variable APIO_HOME_DIR, APIO_PACKAGES_DIR, APIO_PLATFORM.
"""


# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
# pylint: disable=too-many-locals
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
@platforms_option
def cli(
    cmd_ctx: click.core.Context,
    # Options
    project_dir: Path,
    lsftdi: bool,
    lsusb: bool,
    lsserial: bool,
    info: bool,
    platforms: bool,
):
    """Implements the system command. This command executes assorted
    system tools"""

    # Make sure these params are exclusive.
    cmd_util.check_exactly_one_param(
        cmd_ctx, nameof(lsftdi, lsusb, lsserial, info, platforms)
    )

    # Load the various resource files.
    resources = Resources(project_dir=project_dir, project_scope=False)

    # -- Create the system object
    system = System(resources)

    # -- List all connected ftdi devices
    if lsftdi:
        exit_code = system.lsftdi()
        cmd_ctx.exit(exit_code)

    # -- List all connected USB devices
    if lsusb:
        exit_code = system.lsusb()
        cmd_ctx.exit(exit_code)

    # -- List all connected serial devices
    if lsserial:
        exit_code = system.lsserial()
        cmd_ctx.exit(exit_code)

    # -- Show system information
    if info:
        # -- Print platform id.
        click.secho("Platform id     ", nl=False)
        click.secho(resources.platform_id, fg="cyan")

        # -- Print apio package directory.
        click.secho("Python package  ", nl=False)
        click.secho(util.get_path_in_apio_package(""), fg="cyan")

        # -- Print apio home directory.
        click.secho("Apio home       ", nl=False)
        click.secho(util.get_home_dir(), fg="cyan")

        # -- Print apio home directory.
        click.secho("Apio packages   ", nl=False)
        click.secho(util.get_packages_dir(), fg="cyan")

        cmd_ctx.exit(0)

    if platforms:
        click.secho(
            f"  {'[PLATFORM ID]':18} "
            f"{'[PACKAGE SELECTOR]':20} "
            f"{'[DESCRIPTION]'}",
            fg="magenta",
        )
        for platform_id, platform_info in resources.platforms.items():
            description = platform_info.get("description")
            package_selector = platform_info.get("package_selector")
            this_package = platform_id == resources.platform_id
            fg = "green" if this_package else None
            click.secho(
                f"  {platform_id:18} {package_selector:20} {description}",
                fg=fg,
            )
        cmd_ctx.exit(0)

    # -- Error, no option selected.
    assert 0, "Non reachable"
