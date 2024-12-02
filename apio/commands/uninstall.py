# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio uninstall' command"""

import sys
from pathlib import Path
from typing import Tuple
from varname import nameof
import click
from apio.managers.old_installer import Installer
from apio import cmd_util
from apio.apio_context import ApioContext
from apio.commands import options, install


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def _uninstall(apio_ctx: ApioContext, packages: list, sayyes, verbose: bool):
    """Uninstall the given list of packages"""

    # -- Ask the user for confirmation
    if sayyes or click.confirm("Do you want to uninstall?"):

        # -- Uninstall packages, one by one
        for package in packages:

            # -- The uninstalation is performed by the Installer object
            modifiers = Installer.Modifiers(
                force=False, checkversion=False, verbose=verbose
            )
            installer = Installer(package, apio_ctx, modifiers)

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
@options.sayyes
@options.verbose_option
def cli(
    cmd_ctx: click.core.Context,
    # Arguments
    packages: Tuple[str],
    # Options
    list_: bool,
    all_: bool,
    project_dir: Path,
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
    cmd_util.check_at_most_one_param(cmd_ctx, nameof(packages, list_, all_))

    # -- Create the apio context.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=False)

    # -- Uninstall the given apio packages
    if packages:
        _uninstall(apio_ctx, packages, sayyes, verbose)
        sys.exit(0)

    # -- Uninstall all the packages
    if all_:
        # -- Get all the installed apio packages
        packages = apio_ctx.profile.packages
        # -- Uninstall them!
        _uninstall(apio_ctx, packages, sayyes, verbose)
        sys.exit(0)

    # -- List all the packages (installed or not)
    if list_:
        # pylint: disable=protected-access
        install._list_packages(apio_ctx)
        # pylint: enable=protected-access
        sys.exit(0)

    # -- Invalid option. Just show the help
    click.secho(cmd_ctx.get_help())
