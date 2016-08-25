# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.scons import SCons


@click.command('sim')
@click.pass_context
def cli(ctx):
    """Launch the verilog simulation."""

    exit_code = SCons().sim()
    ctx.exit(exit_code)
