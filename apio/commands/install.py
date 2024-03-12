"""DOC: TODO"""

# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.installer import Installer
from apio.resources import Resources
from apio import util

# R0801: Similar lines in 2 files
# pylint: disable=R0801
platforms = [
    "linux",
    "linux_x86_64",
    "linux_i686",
    "linux_armv7l",
    "linux_aarch64",
    "windows",
    "windows_x86",
    "windows_amd64",
    "darwin",
    "darwin_arm64",
]


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


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
# pylint: disable=W0622
@click.command("install", context_settings=util.context_settings())
@click.pass_context
@click.argument("packages", nargs=-1)
@click.option("-a", "--all", is_flag=True, help="Install all packages.")
@click.option(
    "-l", "--list", is_flag=True, help="List all available packages."
)
@click.option(
    "-f", "--force", is_flag=True, help="Force the packages installation."
)
@click.option(
    "-p",
    "--platform",
    type=click.Choice(platforms),
    metavar="",
    help=(
        f"Set the platform [{', '.join(platforms)}] "
        "(Advanced, for developers)."
    ),
)
def cli(ctx, packages: tuple, all: bool, list: bool, force: bool, platform):
    """Install apio packages."""

    # -- Install the given apio packages
    if packages:
        install_packages(packages, platform, force)

    # -- Install all the available packages
    elif all: 

        # -- Get all the resources
        resources = Resources(platform)

        # -- Install all the available packages for this platform!
        install_packages(resources.packages, platform, force)

    # -- List all the packages (installed or not)
    elif list:
        # -- Get all the resources
        resources = Resources(platform)

        # -- List the packages
        resources.list_packages()

    # -- Invalid option. Just show the help
    else:
        click.secho(ctx.get_help())
