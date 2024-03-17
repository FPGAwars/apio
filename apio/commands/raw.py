# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO RAW command"""

import click
from apio import util


@click.command("raw", context_settings=util.context_settings())
@click.pass_context
@click.argument("cmd")
def cli(ctx, cmd):
    """Execute commands directly from the Apio packages"""

    exit_code = util.call(cmd)
    ctx.exit(exit_code)
