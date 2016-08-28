# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from pkg_resources import get_distribution

from apio.util import get_pypi_latest_version


@click.command('upgrade')
@click.pass_context
def cli(ctx):
    """Check the latest Apio version."""

    current_version = get_distribution('apio').version
    latest_version = get_pypi_latest_version()

    if latest_version is None:
        ctx.exit(1)

    if latest_version == current_version:
        click.secho('You\'re up-to-date!\nApio {} is currently the '
                    'newest version available.'.format(latest_version),
                    fg='green')
    else:
        click.secho('You\'re not updated\nPlease execute '
                    '`pip install -U apio` to upgrade.',
                    fg="yellow")
