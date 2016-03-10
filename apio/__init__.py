#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .util import get_systype
from .execute import run_scons
from .packages.scons import SconsInstaller
from .packages.icestorm import IcestormInstaller
from .packages.driver import DriverInstaller


@click.group()
@click.version_option()
def cli():
    """
    """


@cli.command('debug')
def debug():
    print('Platform: ' + get_systype())


@cli.group()
def install():
    """
    """


@install.command('toolchain')
def install_toolchain():
    SconsInstaller().install()
    IcestormInstaller().install()


@install.command('drivers')
def install_drivers():
    DriverInstaller().install()


@cli.group()
def uninstall():
    """
    """


@uninstall.command('toolchain')
def uninstall_toolchain():
    key = raw_input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        SconsInstaller().uninstall()
        IcestormInstaller().uninstall()


@uninstall.command('drivers')
def uninstall_drivers():
    key = raw_input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        DriverInstaller().uninstall()


@cli.command('clean')
def clean():
    run_scons(['-c'])


@cli.command('build')
def build():
    run_scons()


@cli.command('upload')
def upload():
    run_scons(['upload'])


@cli.command('time')
def time():
    run_scons(['time'])


@cli.command('sim')
def sim():
    run_scons(['sim'])


if __name__ == '__main__':
    cli()
