# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Main implementation of APIO INSTALL command"""

import click
from apio.managers.installer import Installer
from apio.resources import Resources
from apio import util

# ------------------
# -- CONSTANTS
# ------------------
CMD = "install"  # -- Comand name
PACKAGES = "packages"  # -- Argument
ALL = "all"  # -- Option
LIST = "list"  # -- Option
FORCE = "force"  # -- Option
PLATFORM = "platform"  # -- Option


def install_packages(packages: list, platform: str, force: bool):
    """Install the apio packages passed as a list
    * INPUTS:
      - packages: List of packages (Ex. ['examples', 'oss-cad-suite'])
      - platform: Specific platform (Advanced, just for developers)
      - force: Force package installation
    """
    # -- Install packages, one by one...
    for package in packages:

        # -- The instalation is performed by the Installer object
        inst = Installer(package, platform, force)

        # -- Install the package!
        inst.install()


@click.command(CMD, context_settings=util.context_settings())
@click.pass_context
@click.argument(PACKAGES, nargs=-1)
@click.option("-a", f"--{ALL}", is_flag=True, help="Install all packages.")
@click.option(
    "-l", f"--{LIST}", is_flag=True, help="List all available packages."
)
@click.option(
    "-f", f"--{FORCE}", is_flag=True, help="Force the packages installation."
)
@click.option(
    "-p",
    f"--{PLATFORM}",
    type=click.Choice(util.PLATFORMS),
    metavar="",
    help=(
        f"Set the platform [{', '.join(util.PLATFORMS)}] "
        "(Advanced, for developers)."
    ),
)
def cli(ctx, **kwargs):
    """Install apio packages."""

    # -- Extract the arguments
    packages = kwargs[PACKAGES]  # -- tuple
    platform = kwargs[PLATFORM]  # -- str
    _all = kwargs[ALL]  # -- bool
    _list = kwargs[LIST]  # -- bool
    force = kwargs[FORCE]  # -- bool

    # -- Install the given apio packages
    if packages:
        install_packages(packages, platform, force)

    # -- Install all the available packages (if any)
    elif _all:

        # -- Get all the resources
        resources = Resources(platform)

        # -- Install all the available packages for this platform!
        install_packages(resources.packages, platform, force)

    # -- List all the packages (installed or not)
    elif _list:
        # -- Get all the resources
        resources = Resources(platform)

        # -- List the packages
        resources.list_packages()

    # -- Invalid option. Just show the help
    else:
        click.secho(ctx.get_help())
