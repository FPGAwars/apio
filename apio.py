#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click

from install import Installer


@click.group()
@click.version_option()
def cli():
    """
    """


@cli.command('install')
@click.argument('name')
def install(name):
    if name == 'icestorm':
        Installer().install()
        click.echo('Install %s' % name)
    else:
        click.echo('Toolchain %s not found' % name, err=True)


@cli.command('clean')
def clean(name):
    pass


@cli.command('build')
def build(name):
    pass


@cli.command('upload')
def upload(name):
    pass


@cli.command('time')
def time(name):
    pass


@cli.command('sim')
def sim(name):
    pass
