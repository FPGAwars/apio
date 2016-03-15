#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .util import get_systype
from .execute import SConsExecute
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
    SConsExecute().run_scons(['-c'])


@cli.command('build')
def build():
    """Synthesize the bitstream."""
    SConsExecute().run_scons()


@cli.command('upload')
def upload():
    """Upload bitstream to FPGA."""
    SConsExecute().run_scons(['upload'])


@cli.command('time')
def time():
    """Bitstream timing analysis."""
    SConsExecute().run_scons(['time'])


@cli.command('sim')
def sim():
    """Launch verilog simulation."""
    SConsExecute().run_scons(['sim'])


if __name__ == '__main__':
    cli()
