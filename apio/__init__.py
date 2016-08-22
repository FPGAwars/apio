# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click
from sys import exit as sys_exit

from .util import get_systype
from .examples import Examples
from .execute import SCons, System
from .project import Project
from .resources import Resources
from .drivers import Drivers
from .installer import Installer

# Python3 compat
try:
    unicode = str
except NameError:  # pragma: no cover
    pass


@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option()
def cli(ctx):
    """
    Environment for icestorm toolchain management
    """

    # Update help structure
    if ctx.invoked_subcommand is None:
        env_help = []
        env_commands = ['boards', 'drivers', 'examples', 'init',
                        'install', 'system', 'uninstall']

        help = ctx.get_help()
        help = help.split('\n')

        # Find env commands' lines
        for line in list(help):
            for command in env_commands:
                if (' ' + command) in line:
                    help.remove(line)
                    env_help.append(line)

        help = '\n'.join(help)
        help = help.replace('Commands:\n', 'Code commands:\n')
        help += "\n\nEnvironment commands:\n"
        help += '\n'.join(env_help)

        click.secho(help)


# -- Environment commands


@cli.command('install')
@click.pass_context
@click.argument('packages', nargs=-1)
@click.option('-a', '--all', is_flag=True,
              help='Install all packages.')
@click.option('-l', '--list', is_flag=True,
              help='List all available packages.')
def install(ctx, packages, all, list):
    """Install packages."""

    if packages:
        for package in packages:
            Installer(package).install()
    elif all:
        packages = Resources().packages
        for package in packages:
            Installer(package).install()
    elif list:
        Resources().list_packages(installed=True, notinstalled=True)
    else:
        click.secho(ctx.get_help())


@cli.command('uninstall')
@click.pass_context
@click.argument('packages', nargs=-1)
@click.option('-a', '--all', is_flag=True,
              help='Uninstall all packages.')
@click.option('-l', '--list', is_flag=True,
              help='List all installed packages.')
def uninstall(ctx, packages, all, list):
    """Uninstall packages."""

    if packages:
        _uninstall(packages)
    elif all:
        packages = Resources().packages
        _uninstall(packages)
    elif list:
        Resources().list_packages(installed=True, notinstalled=False)
    else:
        click.secho(ctx.get_help())


def _uninstall(packages):
    if click.confirm('Do you want to continue?'):
        for package in packages:
            Installer(package).uninstall()
    else:
        click.secho('Abort!', fg='red')


@cli.command('drivers')
@click.pass_context
@click.option('-e', '--enable', is_flag=True,
              help='Enable FPGA drivers')
@click.option('-d', '--disable', is_flag=True,
              help='Disable FPGA drivers')
def drivers(ctx, enable, disable):
    """Drivers for the FPGAs."""

    if enable:
        Drivers().enable()
    elif disable:
        Drivers().disable()
    else:
        click.secho(ctx.get_help())


@cli.command('boards')
@click.pass_context
@click.option('-l', '--list', is_flag=True,
              help='List all supported FPGA boards.')
def boards(ctx, list):
    """Manage FPGA boards."""

    if list:
        Resources().list_boards()
    else:
        click.secho(ctx.get_help())


@cli.command('init')
@click.pass_context
@click.option('-s', '--scons', is_flag=True,
              help='Create default SConstruct file.')
@click.option('-b', '--board', type=unicode, metavar='BOARD',
              help='Create init file with the selected board.')
@click.option('--project-dir', type=unicode, metavar='PATH',
              help='Set the target directory for the project')
def init(ctx, board, scons, project_dir):
    """Create a new apio project."""

    if scons:
        Project().create_sconstruct(project_dir)
    elif board:
        Project().new_ini(board, project_dir)
    else:
        click.secho(ctx.get_help())


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


@system.command('platform')
def platform():
    """Show system information."""
    click.secho('Platform: ', nl=False)
    click.secho(get_systype(), fg='green')


# -- Code commands


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

    # Run scons
    exit_code = SCons().build({
        'board': board,
        'fpga': fpga,
        'size': size,
        'type': type,
        'pack': pack
    })
    ctx.exit(exit_code)

# Advances notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-build


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
    """Upload the bitstream to the FPGA."""

    # Run scons
    exit_code = SCons().upload({
        'board': board,
        'fpga': fpga,
        'size': size,
        'type': type,
        'pack': pack
    }, device)
    ctx.exit(exit_code)

# Advances notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-upload


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

    # Run scons
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
    """Launch the verilog simulation."""
    exit_code = SCons().sim()
    ctx.exit(exit_code)


if __name__ == '__main__':
    sys_exit(cli())
