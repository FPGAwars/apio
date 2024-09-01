# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO UNINSTALL command"""

from pathlib import Path
import click
from apio.managers.installer import Installer, list_packages
from apio.profile import Profile
from apio import util
from apio.resources import Resources


# ------------------
# -- CONSTANTS
# ------------------
CMD = "uninstall"  # -- Comand name
PROJECT_DIR = "project_dir"  # -- Option
PACKAGES = "packages"  # -- Argument
ALL = "all"  # -- Option
LIST = "list"  # -- Option
PLATFORM = "platform"  # -- Option


def _uninstall(packages: list, platform: str, resources: Resources):
    """Uninstall the given list of packages"""

    # -- Ask the user for confirmation
    if click.confirm("Do you want to continue?"):

        # -- Uninstall packages, one by one
        for package in packages:

            # -- The uninstalation is performed by the Installer object
            modifiers = Installer.Modifiers(force=False, checkversion=False)
            installer = Installer(package, platform, resources, modifiers)

            # -- Uninstall the package!
            installer.uninstall()

    # -- User quit!
    else:
        click.secho("Abort!", fg="red")


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.argument(PACKAGES, nargs=-1)
@click.option(
    "-p",
    "--project-dir",
    type=Path,
    metavar="str",
    help="Set the target directory for the project.",
)
@click.option("-a", f"--{ALL}", is_flag=True, help="Uninstall all packages.")
@click.option(
    "-l", f"--{LIST}", is_flag=True, help="List all installed packages."
)
@click.option(
    "-p",
    f"--{PLATFORM}",
    type=click.Choice(util.PLATFORMS),
    help=(
        f"Set the platform [{', '.join(util.PLATFORMS)}] "
        "(Advanced, for developers)."
    ),
)
def cli(ctx, **kwargs):
    """Uninstall packages."""

    # -- Extract the arguments
    packages = kwargs[PACKAGES]  # -- tuple
    platform = kwargs[PLATFORM]  # -- str
    _all = kwargs[ALL]  # -- bool
    _list = kwargs[LIST]  # -- bool
    project_dir = kwargs[PROJECT_DIR]  # -- str

    # -- Load the resources.
    resources = Resources(platform=platform, project_dir=project_dir)

    # -- Uninstall the given apio packages
    if packages:
        _uninstall(packages, platform, resources)

    # -- Uninstall all the packages
    elif _all:

        # -- Get all the installed apio packages
        packages = Profile().packages

        # -- Uninstall them!
        _uninstall(packages, platform, resources)

    # -- List all the packages (installed or not)
    elif _list:
        list_packages(platform)

    # -- Invalid option. Just show the help
    else:
        click.secho(ctx.get_help())
