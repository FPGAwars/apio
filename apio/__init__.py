#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import click
import subprocess

from .util import get_systype
from .installer import Installer
from .packages.icestorm import IcestormInstaller
from .packages.scons import SconsInstaller
from .packages.rules import RulesInstaller

# Give the priority to the packages installed by apio
os.environ['PATH'] = (
    os.path.join(Installer.packages_dir, 'toolchain-icestorm', 'bin') + ":" +
    os.path.join(Installer.packages_dir, 'tool-scons', 'script') + ":" +
    os.environ['PATH'])


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
    SconsInstaller().install()
    RulesInstaller().install()


@cli.command('uninstall')
def uninstall():
    key = raw_input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        IcestormInstaller().uninstall()
        SconsInstaller().uninstall()
        RulesInstaller().uninstall()


@cli.command('clean')
def clean():
    subprocess.call(['scons', '-c'])


@cli.command('build')
def build():
    subprocess.call(['scons'])


@cli.command('upload')
def upload():
    subprocess.call(['scons', 'upload'])


@cli.command('time')
def time():
    subprocess.call(['scons', 'time'])


@cli.command('sim')
def sim():
    subprocess.call(['scons', 'sim'])
