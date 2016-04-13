#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .util import get_systype
from .execute import SCons, System
from .packages.scons import SconsInstaller
from .packages.icestorm import IcestormInstaller
from .packages.driver import DriverInstaller
from .packages.system import SystemInstaller

try:
    input = raw_input
except NameError:
    pass


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


# System #


@cli.group()
def system():
    """System development tools.\n
       Install with `apio install system`."""


@system.command('lsusb')
def lsusb():
    """List all connected USB devices."""
    System().lsusb()


@system.command('lsftdi')
def lsftdi():
    """List all connected FTDI devices."""
    System().lsftdi()


# Install #


@cli.group('install', invoke_without_command=True)
@click.pass_context
@click.option('--all', is_flag=True, help='Install all toolchains.')
def install(ctx, all):
    """Install development tools."""
    if ctx.invoked_subcommand is None:
        SystemInstaller().install()
        SconsInstaller().install()
        IcestormInstaller().install()


@install.command('driver')
def install_driver():
    """Install open FPGA drivers."""
    DriverInstaller().install()


@install.command('system')
def install_system():
    """Install system development tools."""
    SystemInstaller().install()


@install.command('scons')
def install_scons():
    """Install scons toolchain."""
    SconsInstaller().install()


@install.command('icestorm')
def install_icestorm():
    """Install icestorm toolchain."""
    IcestormInstaller().install()


# Uninstall #


@cli.group('uninstall', invoke_without_command=True)
@click.pass_context
@click.option('--all', is_flag=True, help='Uninstall all toolchains.')
def uninstall(ctx, all):
    """Uninstall development tools."""
    if ctx.invoked_subcommand is None:
        _uninstall(SystemInstaller().uninstall,
                   SconsInstaller().uninstall,
                   IcestormInstaller().uninstall)


@uninstall.command('driver')
def uninstall_driver():
    """Uninstall open FPGA drivers."""
    _uninstall(DriverInstaller().uninstall)


@uninstall.command('system')
def uninstall_system():
    """Uninstall system development tools."""
    _uninstall(SystemInstaller().uninstall)


@uninstall.command('scons')
def uninstall_scons():
    """Uninstall scons toolchain."""
    _uninstall(SconsInstaller().uninstall)


@uninstall.command('icestorm')
def uninstall_icestorm():
    """Uninstall icestorm toolchain."""
    _uninstall(IcestormInstaller().uninstall)


def _uninstall(*functions):
    key = input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        for count, function in enumerate(functions):
            function()


# Synthesize #


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
