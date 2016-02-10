#!/usr/bin/env python
# -*- coding: utf-8 -*-

import click
import subprocess

from install import Installer
from os.path import join, expanduser

package_dir = join(expanduser("~"), '.platformio/packages/')


@click.group()
@click.version_option()
def cli():
    """
    """


@cli.command('install')
def install():
    installer = Installer(package_dir)
    print('Install tool-scons')
    installer.install('tool-scons', True)
    print('Install toolchain-icestorm')
    installer.install('toolchain-icestorm')


@cli.command('clean')
def clean():
    subprocess.call(['python', join(package_dir, 'tool-scons', 'script', 'scons'), '-c'])


@cli.command('build')
def build():
    subprocess.call(['python', join(package_dir, 'tool-scons', 'script', 'scons')])


@cli.command('upload')
def upload():
    subprocess.call(['python', join(package_dir, 'tool-scons', 'script', 'scons'), "upload"])
