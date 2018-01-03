# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.profile import Profile


@click.command('config')
@click.pass_context
@click.option('-l', '--list', is_flag=True,
              help='List all configuration parameters.')
@click.option('-v', '--verbose', type=click.Choice(['0', '1']),
              help='Verbose mode: `0` General, `1` Information.')
@click.option('-e', '--exe', type=click.Choice(['default', 'native']),
              help='Configure executables: `default` selects apio packages, ' +
                   '`native` selects system binaries.')
def cli(ctx, list, verbose, exe):
    """Apio configuration."""

    if list:  # pragma: no cover
        profile = Profile()
        profile.list()
    elif verbose:  # pragma: no cover
        profile = Profile()
        profile.add_config('verbose', verbose)
    elif exe:  # pragma: no cover
        profile = Profile()
        profile.add_config('exe', exe)
    else:
        click.secho(ctx.get_help())
