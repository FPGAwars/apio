# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.scons import SCons

# Python3 compat
import sys
if (sys.version_info > (3, 0)):
    unicode = str


@click.command('build')
@click.pass_context
@click.option('-b', '--board', type=unicode, metavar='board',
              help='Set the board.')
@click.option('--fpga', type=unicode, metavar='fpga',
              help='Set the FPGA.')
@click.option('--size', type=unicode, metavar='size',
              help='Set the FPGA type (1k/8k).')
@click.option('--type', type=unicode, metavar='type',
              help='Set the FPGA type (hx/lp).')
@click.option('--pack', type=unicode, metavar='package',
              help='Set the FPGA package.')
@click.option('-p', '--project-dir', type=unicode, metavar='path',
              help='Set the target directory for the project.')
@click.option('-v', '--verbose', is_flag=True,
              help='Show the entire output of the command.')
@click.option('--verbose-yosys', is_flag=True,
              help='Show the yosys output of the command.')
@click.option('--verbose-arachne', is_flag=True,
              help='Show the arachne output of the command.')
def cli(ctx, board, fpga, pack, type, size, project_dir,
        verbose, verbose_yosys, verbose_arachne):
    """Synthesize the bitstream."""

    # Run scons
    exit_code = SCons(project_dir).build({
        'board': board,
        'fpga': fpga,
        'size': size,
        'type': type,
        'pack': pack,
        'verbose': {
            'all': verbose,
            'yosys': verbose_yosys,
            'arachne': verbose_arachne
        }
    })
    ctx.exit(exit_code)

# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-build
