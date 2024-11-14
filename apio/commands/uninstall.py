# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio uninstall' command"""

from pathlib import Path
from typing import Tuple
from varname import nameof
import click
from click.core import Context
from apio.managers.installer import Installer
from apio.profile import Profile
from apio import cmd_util
from apio.resources import Resources
from apio.commands import options


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def _uninstall(
    packages: list, platform: str, resources: Resources, sayyes, verbose: bool
):
    """Uninstall the given list of packages"""

    # -- Ask the user for confirmation
    if sayyes or click.confirm("Do you want to uninstall?"):

        # -- Uninstall packages, one by one
        for package in packages:

            # -- The uninstalation is performed by the Installer object
            modifiers = Installer.Modifiers(
                force=False, checkversion=False, verbose=verbose
            )
            installer = Installer(package, platform, resources, modifiers)

            # -- Uninstall the package!
            installer.uninstall()

    # -- User quit!
    else:
        click.secho("Abort!", fg="red")


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The command 'apio uninstall' has been deprecated. Please use the
command 'apio packages' instead.
"""


# pylint: disable=duplicate-code
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    "uninstall",
    short_help="[Depreciated] Uninstall apio packages.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@click.argument("packages", nargs=-1, required=False)
@options.list_option_gen(help="List all installed packages.")
@options.all_option_gen(help="Uninstall all packages.")
@options.project_dir_option
@options.platform_option
@options.sayyes
@options.verbose_option
def cli(
    ctx: Context,
    # Arguments
    packages: Tuple[str],
    # Options
    list_: bool,
    all_: bool,
    project_dir: Path,
    platform: str,
    sayyes: bool,
    verbose: bool,
):
    """Implements the uninstall command."""

    click.secho(
        "The 'apio uninstall' command is deprecated. "
        "Please use the 'apio packages' command instead.",
        fg="yellow",
    )

    # Make sure these params are exclusive.
    cmd_util.check_at_most_one_param(ctx, nameof(packages, list_, all_))

    # -- Load the resources.
    resources = Resources(
        platform=platform,
        project_dir=project_dir,
        project_scope=False,
    )

    # -- Uninstall the given apio packages
    if packages:
        _uninstall(packages, platform, resources, sayyes, verbose)
        ctx.exit(0)

    # -- Uninstall all the packages
    if all_:
        # -- Get all the installed apio packages
        packages = Profile().packages
        # -- Uninstall them!
        _uninstall(packages, platform, resources, sayyes, verbose)
        ctx.exit(0)

    # -- List all the packages (installed or not)
    if list_:
        resources.list_packages()
        ctx.exit(0)

    # -- Invalid option. Just show the help
    click.secho(ctx.get_help())
