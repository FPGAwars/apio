# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.scons import SCons


@click.command('clean')
@click.pass_context
def cli(ctx):
    """Clean the previous generated files."""
    exit_code = SCons().clean()
    ctx.exit(exit_code)
