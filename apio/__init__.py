#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import click
import subprocess

from install import Installer
from os.path import join, expanduser, dirname, isfile

package_dir = join(expanduser("~"), '.platformio/packages/')
scons_dir = join(package_dir, 'tool-scons', 'script', 'scons')
rules_local_path = join(dirname(__file__), 'rules', '80-icestick.rules')
rules_system_path = '/etc/udev/rules.d/80-icestick.rules'

# -- Give the priority to the packages installed by apio
os.environ['PATH'] = (join(package_dir, 'toolchain-icestorm', 'bin') +
                      ":" + os.environ['PATH'])


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

    print('Install icestick.rules')
    if not isfile(rules_system_path):
        print rules_local_path
        subprocess.call(['sudo', 'cp', rules_local_path, rules_system_path])
    else:
        print('Package icestick.rules is already the newest version')


@cli.command('uninstall')
def uninstall():
    key = raw_input('Are you sure? [Y/N]: ')
    if key == 'y' or key == 'Y':
        installer = Installer(package_dir)
        installer.uninstall('tool-scons')
        installer.uninstall('toolchain-icestorm')

        if isfile(rules_system_path):
            print('Uninstall package icestick.rules')
            subprocess.call(['sudo', 'rm', rules_system_path])
        else:
            print('Package icestick.rules is not installed')


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
