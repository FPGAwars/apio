# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.scons import SCons


@click.command('verify')
@click.pass_context
def cli(ctx):
    """Verify the verilog code."""
    exit_code = SCons().verify()
    ctx.exit(exit_code)
