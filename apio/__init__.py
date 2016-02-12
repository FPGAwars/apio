#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import click
import subprocess

from install import Installer
from os.path import join, expanduser

package_dir = join(expanduser("~"), '.platformio/packages/')
scons_dir = join(package_dir, 'tool-scons', 'script', 'scons')
os.environ['PATH'] = os.environ['PATH'] + ":" + join(package_dir, 'toolchain-icestorm', 'bin')


@click.group()
@click.version_option()
def cli():
    """
    """


@cli.command('install')
def install():
    installer = Installer(package_dir)
    installer.install('tool-scons')
    installer.install('toolchain-icestorm')


@cli.command('uninstall')
def uninstall():
    key = raw_input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        installer = Installer(package_dir)
        installer.uninstall('tool-scons')
        installer.uninstall('toolchain-icestorm')


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
