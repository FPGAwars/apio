# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO INSTALL command"""

from pathlib import Path
import click
from apio.managers.installer import Installer, list_packages
from apio.resources import Resources
from apio import util
from apio.commands import options


def install_packages(
    packages: list, platform: str, resources: Resources, force: bool
):
    """Install the apio packages passed as a list
    * INPUTS:
      - packages: List of packages (Ex. ['examples', 'oss-cad-suite'])
      - platform: Specific platform (Advanced, just for developers)
      - force: Force package installation
    """
    # -- Install packages, one by one...
    for package in packages:

        # -- The instalation is performed by the Installer object
        modifiers = Installer.Modifiers(force=force, checkversion=True)
        installer = Installer(package, platform, resources, modifiers)

        # -- Install the package!
        installer.install()


# ---------------------------
# -- COMMAND
# ---------------------------
# R0913: Too many arguments (7/5)
# pylint: disable=R0913
@click.command("install", context_settings=util.context_settings())
@click.pass_context
@click.argument("packages", nargs=-1)
@options.project_dir_option
@options.all_option_gen(help="Install all packages.")
@options.list_option_gen(help="List all available packages.")
@options.force_option_gen(help="Force the packages installation.")
@options.platform_option
def cli(
    ctx,
    # Arguments
    packages,
    # Options
    project_dir: Path,
    all_: bool,
    list_: bool,
    force: bool,
    platform: str,
):
    """Install apio packages."""

    # -- Load the resources.
    resources = Resources(platform=platform, project_dir=project_dir)

    # -- Install the given apio packages
    if packages:
        install_packages(packages, platform, resources, force)

    # -- Install all the available packages (if any)
    elif all_:
        # -- Install all the available packages for this platform!
        install_packages(resources.packages, platform, resources, force)

    # -- List all the packages (installed or not)
    elif list_:
        list_packages(platform)

    # -- Invalid option. Just show the help
    else:
        click.secho(ctx.get_help())
