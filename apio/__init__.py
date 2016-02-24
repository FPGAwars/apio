#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import subprocess

from .util import get_systype
from .packages.icestorm import IcestormInstaller


@click.group()
@click.version_option()
def cli():
    """
    """


@cli.command('debug')
def debug():
    print('Platform: ' + get_systype())


@cli.command('install')
def install():
    IcestormInstaller().install()


@cli.command('uninstall')
def uninstall():
    key = raw_input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        IcestormInstaller().uninstall()


@cli.command('clean')
def clean():
    subprocess.call(['python', scons_dir, '-c'])


@cli.command('build')
def build():
    subprocess.call(['python', scons_dir])


@cli.command('upload')
def upload():
    subprocess.call(['python', scons_dir, "upload"])


@cli.command('time')
def time():
    subprocess.call(['python', scons_dir, "time"])


@cli.command('sim')
def sim():
    subprocess.call(['python', scons_dir, "sim"])
