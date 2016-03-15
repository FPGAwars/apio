#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .util import get_systype
from .execute import SCons
from .packages.scons import SconsInstaller
from .packages.icestorm import IcestormInstaller
from .packages.driver import DriverInstaller


@click.group()
@click.version_option()
def cli():
    """
    Environment for icestorm toolchain management
    """


@cli.command('debug')
def debug():
    """Show system information."""
    print('Platform: ' + get_systype())


@cli.command('init')
def init():
    """Creates default SConstruct file."""
    SCons().create_sconstruct()


@cli.command('install')
@click.option('--driver', is_flag=True)
def install(driver):
    """Install icestorm toolchain."""
    if (driver):
        DriverInstaller().install()
    else:
        SconsInstaller().install()
        IcestormInstaller().install()


@cli.command('uninstall')
@click.option('--driver', is_flag=True)
def uninstall(driver):
    """Uninstall icestorm toolchain."""
    key = raw_input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        if (driver):
            DriverInstaller().uninstall()
        else:
            SconsInstaller().uninstall()
            IcestormInstaller().uninstall()


@cli.command('clean')
def clean():
    """Remove previous bitstream."""
    SCons().run(['-c'])


@cli.command('build')
def build():
    """Synthesize the bitstream."""
    SCons().run()


@cli.command('upload')
def upload():
    """Upload bitstream to FPGA."""
    SCons().run(['upload'])


@cli.command('time')
def time():
    """Bitstream timing analysis."""
    SCons().run(['time'])


@cli.command('sim')
def sim():
    """Launch verilog simulation."""
    SCons().run(['sim'])


if __name__ == '__main__':
    cli()
