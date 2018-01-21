# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.scons import SCons
from apio.managers.drivers import Drivers

# Python3 compat
import sys
if (sys.version_info > (3, 0)):
    unicode = str


@click.command('upload')
@click.pass_context
@click.option('-b', '--board', type=unicode, metavar='board',
              help='Set the board.')
@click.option('--serial-port', type=unicode, metavar='serial-port',
              help='Set the serial port.')
@click.option('--ftdi-id', type=unicode, metavar='ftdi-id',
              help='Set the FTDI id.')
@click.option('-s', '--sram', is_flag=True,
              help='Perform SRAM programming.')
@click.option('-p', '--project-dir', type=unicode, metavar='path',
              help='Set the target directory for the project.')
@click.option('-v', '--verbose', is_flag=True,
              help='Show the entire output of the command.')
@click.option('--verbose-yosys', is_flag=True,
              help='Show the yosys output of the command.')
@click.option('--verbose-arachne', is_flag=True,
              help='Show the arachne output of the command.')
def cli(ctx, board, serial_port, ftdi_id, sram, project_dir,
        verbose, verbose_yosys, verbose_arachne):
    """Upload the bitstream to the FPGA."""

    drivers = Drivers()
    drivers.pre_upload()
    # Run scons
    exit_code = SCons(project_dir).upload({
        'board': board,
        'verbose': {
            'all': verbose,
            'yosys': verbose_yosys,
            'arachne': verbose_arachne
        }
    }, serial_port, ftdi_id, sram)
    drivers.post_upload()
    ctx.exit(exit_code)

# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-upload
