# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.profile import Profile


@click.command('config')
@click.pass_context
@click.option('-l', '--list', is_flag=True,
              help='List all configuration parameters.')
@click.option('-e', '--exe', type=click.Choice(['apio', 'native']),
              help='Configure executables: `apio` selects apio packages, ' +
                   '`native` selects system binaries.')
def cli(ctx, list, exe):
    """Apio configuration."""

    if list:  # pragma: no cover
        profile = Profile()
        exe_mode = profile.get_config_exe()
        click.secho('Executable mode: ' + exe_mode, fg='yellow')
    elif exe:  # pragma: no cover
        profile = Profile()
        profile.add_config(exe)
        profile.save()
        click.secho('Executable mode updated: ' + exe, fg='green')
    else:
        click.secho(ctx.get_help())
