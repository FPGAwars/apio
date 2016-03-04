#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import click
import subprocess

from .util import get_systype
from .installer import Installer
from .packages.icestorm import IcestormInstaller
from .packages.scons import SconsInstaller
from .packages.driver import DriverInstaller

# Give the priority to the packages installed by apio
os.environ['PATH'] = (
    os.path.join(Installer.packages_dir, 'toolchain-icestorm', 'bin') + ":" +
    os.environ['PATH'])

scons_path = os.path.join(Installer.packages_dir, 'tool-scons', 'script', 'scons')


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
    DriverInstaller().install()


@cli.command('uninstall')
def uninstall():
    key = raw_input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        IcestormInstaller().uninstall()
        SconsInstaller().uninstall()
        DriverInstaller().uninstall()


@cli.command('clean')
def clean():
    subprocess.call(['python2', scons_path, '-c'])


@cli.command('build')
def build():
    subprocess.call(['python2', scons_path])


@cli.command('upload')
def upload():
    subprocess.call(['python2', scons_path, 'upload'])


@cli.command('time')
def time():
    subprocess.call(['python2', scons_path, 'time'])


@cli.command('sim')
def sim():
    subprocess.call(['python2', scons_path, 'sim'])
