# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.installer import Installer
from apio.resources import Resources

platforms = ['linux',
             'linux_x86_64',
             'linux_i686',
             'linux_armv7l',
             'linux_aarch64',
             'windows',
             'windows_x86',
             'windows_amd64',
             'darwin']


@click.command('install')
@click.pass_context
@click.argument('packages', nargs=-1)
@click.option('-a', '--all', is_flag=True,
              help='Install all packages.')
@click.option('-l', '--list', is_flag=True,
              help='List all available packages.')
@click.option('-f', '--force', is_flag=True,
              help='Force the packages installation.')
@click.option('-p', '--platform', type=click.Choice(platforms),
              metavar='', help='Set the platform [{}] (Advanced).'.format(
                ', '.join(platforms)))
def cli(ctx, packages, all, list, force, platform):
    """Install packages."""

    if packages:
        for package in packages:
            Installer(package, platform, force).install()
    elif all:  # pragma: no cover
        packages = Resources(platform).packages
        for package in packages:
            Installer(package, platform, force).install()
    elif list:
        Resources(platform).list_packages(installed=True, notinstalled=True)
    else:
        click.secho(ctx.get_help())
