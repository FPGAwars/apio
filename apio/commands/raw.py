# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio import util


@click.command("raw")
@click.pass_context
@click.argument("cmd")
def cli(ctx, cmd):
    """Execute commands directly from the Apio packages"""

    exit_code = util.call(cmd)
    ctx.exit(exit_code)
