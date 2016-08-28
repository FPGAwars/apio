# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.installer import Installer
from apio.resources import Resources


@click.command('install')
@click.pass_context
@click.argument('packages', nargs=-1)
@click.option('-a', '--all', is_flag=True,
              help='Install all packages.')
@click.option('-l', '--list', is_flag=True,
              help='List all available packages.')
def cli(ctx, packages, all, list):
    """Install packages."""

    if packages:
        for package in packages:
            Installer(package).install()
    elif all:  # pragma: no cover
        packages = Resources().packages
        for package in packages:
            if package == 'pio-fpga':  # skip pio-fpga
                continue
            Installer(package).install()
    elif list:
        Resources().list_packages(installed=True, notinstalled=True)
    else:
        click.secho(ctx.get_help())
