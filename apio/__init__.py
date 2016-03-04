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


@cli.command('install')
def install():
    SconsInstaller().install()
    IcestormInstaller().install()
    DriverInstaller().install()


@cli.command('uninstall')
def uninstall():
    key = raw_input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        SconsInstaller().uninstall()
        IcestormInstaller().uninstall()
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
