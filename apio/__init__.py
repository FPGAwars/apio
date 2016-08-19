#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
from sys import exit as sys_exit

from .util import get_systype
from .examples import Examples
from .execute import SCons, System
from .project import Project
from .config import Boards
from .packages.scons import SconsInstaller
from .packages.iverilog import IverilogInstaller
from .packages.icestorm import IcestormInstaller
from .packages.driver import DriverInstaller
from .packages.system import SystemInstaller
from .packages.piofpga import PioFPGAInstaller
from .packages.examples import ExamplesInstaller

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


@cli.command('boards')
def boards():
    """List all the supported FPGA boards."""
    Boards().list()


@cli.command('debug')
def debug():
    """Show system information."""
    click.secho('Platform: ', nl=False)
    click.secho(get_systype(), fg='green')


@cli.command('scons')
def scons():
    """Create default SConstruct file."""
    SCons().create_sconstruct()


@cli.command('init')
@click.pass_context
@click.option('--board', type=unicode, help='Set the FPGA board.')
@click.option('--project-dir', type=unicode, metavar='PATH',
              help='Set the target directory for the project')
def init(ctx, board, project_dir):
    """Create a new apio project."""
    Project().new(board, project_dir)


@cli.command('examples')
@click.pass_context
@click.option('-l', '--list', is_flag=True,
              help='List all available examples.')
@click.option('-d', '--dir', type=unicode, metavar='NAME',
              help='Copy the selected example directory.')
@click.option('-f', '--files', type=unicode, metavar='NAME',
              help='Copy the selected example files.')
@click.option('--project-dir', type=unicode, metavar='PATH',
              help='Set the target directory for the examples')
@click.option('-n', '--sayno', is_flag=True,
              help='Automatically answer NO to all the questions')
def examples(ctx, list, dir, files, project_dir, sayno):
    """Manage default verilog examples.\n
       Install with `apio install examples`"""

    if list:
        Examples().list_examples()
    elif dir:
        Examples().copy_example_dir(dir, project_dir, sayno)
    elif files:
        Examples().copy_example_files(files, project_dir, sayno)
    else:
        click.secho(ctx.get_help())
        click.secho(Examples().examples_of_use_cad())


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
        IverilogInstaller().install()
        IcestormInstaller().install()
        ExamplesInstaller().install()


@install.command('driver')
def install_driver():
    """Install open FPGA drivers."""
    DriverInstaller().install()


@install.command('system')
@click.option('--version',  type=unicode, metavar='version',
    help='Specific version of the package')
def install_system(version):
    """Install system development tools."""
    SystemInstaller().install(version)


@install.command('scons')
@click.option('--version',  type=unicode, metavar='version',
    help='Specific version of the package')
def install_scons(version):
    """Install scons toolchain."""
    SconsInstaller().install(version)

@install.command('iverilog')
@click.option('--version',  type=unicode, metavar='version',
    help='Specific version of the package')
def install_iverilog(version):
    """Install iverilog toolchain."""
    IverilogInstaller().install(version)


@install.command('icestorm')
@click.option('--version',  type=unicode, metavar='version',
    help='Specific version of the package')
def install_icestorm(version):
    """Install icestorm toolchain."""
    IcestormInstaller().install(version)


@install.command('pio-fpga')
@click.option('--version',  type=unicode, metavar='version',
    help='Specific version of the package')
def intall_pio_fpga(version):
    """Install platformio-fpga support."""
    PioFPGAInstaller().install(version)


@install.command('examples')
@click.option('--version',  type=unicode, metavar='version',
    help='Specific version of the package')
def intall_examples(version):
    """Install verilog examples."""
    ExamplesInstaller().install(version)


# Uninstall #

@cli.group('uninstall', invoke_without_command=True)
@click.pass_context
@click.option('--all', is_flag=True, help='Uninstall all toolchains')
def uninstall(ctx, all):
    """Uninstall development tools."""
    if ctx.invoked_subcommand is None:
        _uninstall(SystemInstaller().uninstall,
                   SconsInstaller().uninstall,
                   IverilogInstaller().uninstall,
                   IcestormInstaller().uninstall,
                   ExamplesInstaller().uninstall)


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

@uninstall.command('iverilog')
def uninstall_iverilog():
    """Uninstall iverilog toolchain."""
    _uninstall(IverilogInstaller().uninstall)


@uninstall.command('icestorm')
def uninstall_icestorm():
    """Uninstall icestorm toolchain."""
    _uninstall(IcestormInstaller().uninstall)


@uninstall.command('examples')
def uninstall_examples():
    """Uninstall verilog examples."""
    _uninstall(ExamplesInstaller().uninstall)


def _uninstall(*functions):
    if click.confirm('Do you want to continue?'):
        for count, function in enumerate(functions):
            function()
    else:
        click.secho('Abort!', fg='red')


@cli.command('clean')
def clean():
    """Remove the previous generated files."""
    SCons().clean()


@cli.command('verify')
@click.pass_context
def verify(ctx):
    """Verify the verilog code."""
    exit_code = SCons().verify()
    ctx.exit(exit_code)


@cli.command('build')
@click.pass_context
@click.option('--board', type=unicode, metavar='board',
              help='Set the board')
@click.option('--fpga', type=unicode, metavar='fpga',
              help='Set the FPGA')
@click.option('--size', type=unicode, metavar='size',
              help='Set the FPGA type (1k/8k)')
@click.option('--type', type=unicode, metavar='type',
              help='Set the FPGA type (hx/lp)')
@click.option('--pack', type=unicode, metavar='package',
            help='Set the FPGA package')
def build(ctx, board, fpga, pack, type, size):
    """Synthesize the bitstream."""

    # -- Run scons
    exit_code = SCons().build({
        'board': board,
        'fpga': fpga,
        'size': size,
        'type': type,
        'pack': pack
    })
    ctx.exit(exit_code)

# -- Advances notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-build


@cli.command('upload')
@click.pass_context
@click.option('--device', type=unicode, metavar='board',
              help='Set the board')
@click.option('--board', type=unicode, metavar='board',
              help='Set the board')
@click.option('--fpga', type=unicode, metavar='fpga',
              help='Set the FPGA')
@click.option('--size', type=unicode, metavar='size',
              help='Set the FPGA type (1k/8k)')
@click.option('--type', type=unicode, metavar='type',
              help='Set the FPGA type (hx/lp)')
@click.option('--pack', type=unicode, metavar='package',
            help='Set the FPGA package')
def upload(ctx, device, board, fpga, pack, type, size):
    """Upload bitstream to FPGA."""

    # -- Run scons
    exit_code = SCons().upload({
        'board': board,
        'fpga': fpga,
        'size': size,
        'type': type,
        'pack': pack
    }, device)
    ctx.exit(exit_code)

# -- Advances notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-upload


@cli.command('time')
@click.pass_context
@click.option('--board', type=unicode, metavar='board',
              help='Set the board')
@click.option('--fpga', type=unicode, metavar='fpga',
              help='Set the FPGA')
@click.option('--size', type=unicode, metavar='size',
              help='Set the FPGA type (1k/8k)')
@click.option('--type', type=unicode, metavar='type',
              help='Set the FPGA type (hx/lp)')
@click.option('--pack', type=unicode, metavar='package',
            help='Set the FPGA package')
def time(ctx, board, fpga, pack, type, size):
    """Bitstream timing analysis."""

    # -- Run scons
    exit_code = SCons().time({
        'board': board,
        'fpga': fpga,
        'size': size,
        'type': type,
        'pack': pack
    })
    ctx.exit(exit_code)


@cli.command('sim')
@click.pass_context
def sim(ctx):
    """Launch verilog simulation."""
    exit_code = SCons().sim()
    ctx.exit(exit_code)


if __name__ == '__main__':
    sys_exit(cli())
