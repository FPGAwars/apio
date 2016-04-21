#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from .util import get_systype
from .examples import Examples
from .execute import SCons, System
from .packages.scons import SconsInstaller
from .packages.icestorm import IcestormInstaller
from .packages.driver import DriverInstaller
from .packages.system import SystemInstaller
from .packages.piofpga import PiofpgaInstaller

try:
    input = raw_input
except NameError:
    pass

try:
    unicode = str
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
    """Create default SConstruct file."""
    SCons().create_sconstruct()

EXAMPLE_OF_USE_CAD = """
Example of use:
  apio examples -f leds
Copy the leds example files to the current directory
"""


@cli.command('examples')
@click.pass_context
@click.option('-l', '--list', is_flag=True, help='List all available examples.')
@click.option('-d', '--dir', type=unicode, metavar='NAME',
              help='Copy the selected example directory.')
@click.option('-f', '--files', type=unicode, metavar='NAME',
              help='Copy the selected example files.')
def examples(ctx, list, dir, files):
    """Manage default verilog examples."""
    if list:
        examples = Examples().list_examples()
        print('')
        for example in examples:
            print(' > ' + example)
        print('')
        print('To get and example, use the command:')
        print('apio examples -d/-f name')
        print(EXAMPLE_OF_USE_CAD)
    elif dir:
        Examples().copy_example_dir(dir)
    elif files:
        Examples().copy_example_files(files)
    else:
        print(ctx.get_help())
        print(EXAMPLE_OF_USE_CAD)


# System #


@cli.group()
def system():
    """System development tools.\n
       Install with `apio install system`"""


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
@click.option('--all', is_flag=True, help='Install all toolchains')
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


@install.command('pio-fpga')
def intall_pio_fpga():
    """Install platformio-fpga support."""
    PiofpgaInstaller().install()
    print("> Now execute the following command:")
    print("")
    print("pio platforms install lattice_ice40")


# Uninstall #


@cli.group('uninstall', invoke_without_command=True)
@click.pass_context
@click.option('--all', is_flag=True, help='Uninstall all toolchains')
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
