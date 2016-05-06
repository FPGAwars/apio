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
        IcestormInstaller().install()
        ExamplesInstaller().install()


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
    PioFPGAInstaller().install()


@install.command('examples')
def intall_examples():
    """Install verilog examples."""
    ExamplesInstaller().install()


# Uninstall #


@cli.group('uninstall', invoke_without_command=True)
@click.pass_context
@click.option('--all', is_flag=True, help='Uninstall all toolchains')
def uninstall(ctx, all):
    """Uninstall development tools."""
    if ctx.invoked_subcommand is None:
        _uninstall(SystemInstaller().uninstall,
                   SconsInstaller().uninstall,
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


# Synthesize #
def format_vars(board, pack, type, size):
    """Format the given vars in the form: 'flag=value'"""

    if board is not None:
        board = "board={}".format(board)
    if pack is not None:
        pack = "fpga_pack={}".format(pack)
    if type is not None:
        type = "fpga_type={}".format(type)
    if size is not None:
        size = "fpga_size={}".format(size)

    vars = [f for f in [board, pack, type, size] if f is not None]
    return vars


@cli.command('clean')
def clean():
    """Remove previous bitstream."""
    SCons().run(['-c'])


@cli.command('build')
@click.pass_context
@click.option('--board', type=unicode, metavar='package',
              help='Set the FPGA board')
@click.option('--pack', type=unicode, metavar='package',
              help='Set the FPGA package')
@click.option('--type', type=unicode, metavar='type',
              help='Set the FPGA type (hx/lp)')
@click.option('--size', type=unicode, metavar='size',
              help='Set the FPGA type (1k/8k)')
def build(ctx, board, pack, type, size):
    """Synthesize the bitstream."""

    # -- Get the variables and change them in the form 'flag=value'
    vars = format_vars(board, pack, type, size)

    # -- Run scons
    exit_code = SCons().run(vars)
    ctx.exit(exit_code)

# -- Notes on the Upload target:
# -- (Notes for advanced user)
# --
# -- The upload target first build the project if there was some modification
# --   and then upload the .bin file. For that reason, upload is also a kind
# --   of "build". The same fpga flags than build should be passed.
# --
# --  For example:
# --
# --  apio build --pack vq100
# --
# --  It will create the .bin file for an ice40 hx1k - vq100 FPGA
# --  (like in the nandland go-board)
# --
# --  If now we upload it using:
# --
# --  apio upload
# --
# --  The default flags are used. So the package tq144 is used and the
# --  bitstream is generated again
# --
# -- In order for it to work correctly, we should pass the same flags than
# -- in the build target:
# --
# --  apio upload --pack vq100


@cli.command('upload')
@click.pass_context
@click.option('--board', type=unicode, metavar='package',
              help='Set the FPGA board')
@click.option('--pack', type=unicode, metavar='package',
              help='Set the FPGA package')
@click.option('--type', type=unicode, metavar='type',
              help='Set the FPGA type (hx/lp)')
@click.option('--size', type=unicode, metavar='size',
              help='Set the FPGA type (1k/8k)')
def upload(ctx, board, pack, type, size):
    """Upload bitstream to FPGA."""

    # -- Get the variables and change them in the form 'flag=value'
    vars = format_vars(board, pack, type, size)

    exit_code = SCons().run(['upload'] + vars)
    ctx.exit(exit_code)


@cli.command('time')
@click.pass_context
def time(ctx):
    """Bitstream timing analysis."""
    exit_code = SCons().run(['time'])
    ctx.exit(exit_code)


@cli.command('sim')
@click.pass_context
def sim(ctx):
    """Launch verilog simulation."""
    exit_code = SCons().run(['sim'])
    ctx.exit(exit_code)


if __name__ == '__main__':
    sys_exit(cli())
