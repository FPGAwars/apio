# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Implementation of 'apio install' command"""

import sys
import shutil
from pathlib import Path
from typing import Tuple
from varname import nameof
import click
from apio.managers.old_installer import Installer
from apio.apio_context import ApioContext
from apio import cmd_util
from apio.commands import options


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def _install_packages(
    apio_ctx: ApioContext,
    packages: list,
    force: bool,
    verbose: bool,
):
    """Install the apio packages passed as a list
    * INPUTS:
      - packages: List of packages (Ex. ['examples', 'oss-cad-suite'])
      - platform: Specific platform (Advanced, just for developers)
      - force: Force package installation
      - verbose: Show detailed output.
    """
    # -- Install packages, one by one...
    for package in packages:

        # -- The instalation is performed by the Installer object
        modifiers = Installer.Modifiers(
            force=force, checkversion=True, verbose=verbose
        )
        installer = Installer(package, apio_ctx, modifiers)

        # -- Install the package!
        installer.install()


def _list_packages(apio_ctx: ApioContext, installed=True, notinstalled=True):
    """Print the packages list."""

    # Classify packages
    installed_packages, notinstalled_packages = (
        apio_ctx.get_platform_packages_lists()
    )

    # -- Calculate the terminal width
    terminal_width, _ = shutil.get_terminal_size()

    # -- String with a horizontal line with the same width
    # -- as the terminal
    line = "─" * terminal_width
    dline = "═" * terminal_width

    if installed and installed_packages:

        # ------- Print installed packages table
        # -- Print the header
        click.secho()
        click.secho(dline, fg="green")
        click.secho("Installed packages:", fg="green")

        for package in installed_packages:
            click.secho(line)
            name = click.style(f"{package['name']}", fg="cyan", bold=True)
            version = package["version"]
            description = package["description"]

            click.secho(f"{name} {version}")
            click.secho(f"  {description}")

        click.secho(dline, fg="green")
        click.secho(f"Total: {len(installed_packages)}")

    if notinstalled and notinstalled_packages:

        # ------ Print not installed packages table
        # -- Print the header
        click.secho()
        click.secho(dline, fg="yellow")
        click.secho("Available packages (Not installed):", fg="yellow")

        for package in notinstalled_packages:

            click.secho(line)
            name = click.style(f"{package['name']}", fg="red")
            description = package["description"]
            click.secho(f"{name}  {description}")

        click.secho(dline, fg="yellow")
        click.secho(f"Total: {len(notinstalled_packages)}")

    click.secho("\n")


# ---------------------------
# -- COMMAND
# ---------------------------
HELP = """
The command 'apio install' has been deprecated. Please use the command
'apio packages' command instead.
"""


# pylint: disable=duplicate-code
# pylint: disable=too-many-arguments
# pylint: disable=too-many-positional-arguments
@click.command(
    "install",
    short_help="[Depreciated] Install apio packages.",
    help=HELP,
    cls=cmd_util.ApioCommand,
)
@click.pass_context
@click.argument("packages", nargs=-1, required=False)
@options.list_option_gen(help="List all available packages.")
@options.all_option_gen(help="Install all packages.")
@options.force_option_gen(help="Force the packages installation.")
@options.project_dir_option
@options.verbose_option
def cli(
    cmd_ctx: click.core.Context,
    # Arguments
    packages: Tuple[str],
    # Options
    list_: bool,
    all_: bool,
    force: bool,
    project_dir: Path,
    verbose: bool,
):
    """Implements the install command which allows to
    manage the installation of apio packages.
    """

    click.secho(
        "The 'apio install' command is deprecated. "
        "Please use the 'apio packages' command instead.",
        fg="yellow",
    )

    # Make sure these params are exclusive.
    cmd_util.check_at_most_one_param(cmd_ctx, nameof(packages, all_, list_))

    # -- Create the apio context.
    apio_ctx = ApioContext(project_dir=project_dir, load_project=False)

    # -- Install the given apio packages
    if packages:
        _install_packages(apio_ctx, packages, force, verbose)
        sys.exit(0)

    # -- Install all the available packages (if any)
    if all_:
        # -- Install all the available packages for this platform!
        _install_packages(
            apio_ctx, apio_ctx.platform_packages.keys(), force, verbose
        )
        sys.exit(0)

    # -- List all the packages (installed or not)
    if list_:
        _list_packages(apio_ctx)
        sys.exit(0)

    # -- Invalid option. Just show the help
    click.secho(cmd_ctx.get_help())
