# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.util import get_systype
from apio.managers.system import System


@click.command('system')
@click.pass_context
@click.option('--lsftdi', is_flag=True,
              help='List all connected FTDI devices.')
@click.option('--lsusb', is_flag=True,
              help='List all connected USB devices.')
@click.option('-i', '--info', is_flag=True,
              help='Show system information.')
def cli(ctx, lsftdi, lsusb, info):
    """System tools.\n
       Install with `apio install system`"""

    exit_code = 0

    if lsftdi:
        exit_code = System().lsftdi()
    elif lsusb:
        exit_code = System().lsusb()
    elif info:
        click.secho('Platform: ', nl=False)
        click.secho(get_systype(), fg='yellow')
    else:
        click.secho(ctx.get_help())

    ctx.exit(exit_code)
