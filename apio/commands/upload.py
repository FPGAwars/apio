# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2017 FPGAwars
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
@click.option('-p', '--project-dir', type=unicode, metavar='path',
              help='Set the target directory for the project.')
@click.option('--device', type=unicode, metavar='device',
              help='Set the serial device.')
@click.option('--ftdi-id', type=unicode, metavar='ftdi-id',
              help='Set the FTDI id.')
def cli(ctx, board, project_dir, device, ftdi_id):

    """Upload the bitstream to the FPGA."""

    drivers = Drivers()
    drivers.pre_upload()
    # Run scons
    exit_code = SCons(project_dir).upload({
        'board': board
    }, device, ftdi_id)
    drivers.post_upload()
    ctx.exit(exit_code)

# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-upload
