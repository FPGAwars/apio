# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.installer import Installer
from apio.resources import Resources


@click.command('uninstall')
@click.pass_context
@click.argument('packages', nargs=-1)
@click.option('-a', '--all', is_flag=True,
              help='Uninstall all packages.')
@click.option('-l', '--list', is_flag=True,
              help='List all installed packages.')
def cli(ctx, packages, all, list):
    """Uninstall packages."""

    if packages:
        _uninstall(packages)
    elif all:  # pragma: no cover
        packages = Resources().packages
        _uninstall(packages)
    elif list:
        Resources().list_packages(installed=True, notinstalled=False)
    else:
        click.secho(ctx.get_help())


def _uninstall(packages):
    if click.confirm('Do you want to continue?'):
        for package in packages:
            if package == 'pio-fpga':  # skip pio-fpga
                continue
            Installer(package).uninstall()
    else:
        click.secho('Abort!', fg='red')
