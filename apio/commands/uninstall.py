# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO UNINSTALL command"""

import click
from apio.managers.installer import Installer, list_packages
from apio.profile import Profile
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "uninstall"  # -- Comand name
PACKAGES = "packages"  # -- Argument
ALL = "all"  # -- Option
LIST = "list"  # -- Option
PLATFORM = "platform"  # -- Option


def _uninstall(packages: list, platform: str):
    """Uninstall the given list of packages"""

    # -- Ask the user for confirmation
    if click.confirm("Do you want to continue?"):

        # -- Uninstall packages, one by one
        for package in packages:

            # -- The uninstalation is performed by the Installer object
            inst = Installer(package, platform, checkversion=False)

            # -- Uninstall the package!
            inst.uninstall()

    # -- User quit!
    else:
        click.secho("Abort!", fg="red")


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.argument(PACKAGES, nargs=-1)
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

    # -- Uninstall the given apio packages
    if packages:
        _uninstall(packages, platform)

    # -- Uninstall all the packages
    elif _all:

        # -- Get all the installed apio packages
        packages = Profile().packages

        # -- Uninstall them!
        _uninstall(packages, platform)

    # -- List all the packages (installed or not)
    elif _list:
        list_packages(platform)

    # -- Invalid option. Just show the help
    else:
        click.secho(ctx.get_help())
