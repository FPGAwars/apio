# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click
import subprocess

from os.path import join, dirname, isfile

from apio.util import get_systype

platform = get_systype()


class Drivers(object):  # pragma: no cover

    rules_local_path = join(
        dirname(__file__), '..', 'resources', '80-icestick.rules')
    rules_system_path = '/etc/udev/rules.d/80-icestick.rules'

    def enable(self):
        if 'linux' in platform:
            self._enable_linux()
        elif 'darwin' in platform:
            self._enable_darwin()
        elif 'windows' in platform:
            self._enable_windows()

    def disable(self):
        if 'linux' in platform:
            self._disable_linux()
        elif 'darwin' in platform:
            self._disable_darwin()
        elif 'windows' in platform:
            self._disable_windows()

    def _enable_linux(self):
        click.secho('Configure FTDI drivers for FPGA')
        if not isfile(self.rules_system_path):
            subprocess.call(['sudo', 'cp',
                             self.rules_local_path, self.rules_system_path])
            subprocess.call(['sudo', 'service', 'udev', 'restart'])
            click.secho('FPGA drivers enabled', fg='green')
        else:
            click.secho('Already enabled', fg='yellow')

    def _disable_linux(self):
        if isfile(self.rules_system_path):
            click.secho('Revert FTDI drivers\' configuration')
            subprocess.call(['sudo', 'rm', self.rules_system_path])
            click.secho('FPGA drivers disabled', fg='yellow')
        else:
            click.secho('Already disabled', fg='red')

    def _enable_darwin(self):
        # TODO: return if brew is not installed
        subprocess.call(['brew', 'install', 'libftdi'])
        click.secho('Configure FTDI drivers for FPGA')
        subprocess.call(['sudo', 'kextunload', '-b',
                         'com.FTDI.driver.FTDIUSBSerialDriver'])
        subprocess.call(['sudo', 'kextunload', '-b',
                         'com.apple.driver.AppleUSBFTDI'])
        click.secho('FPGA drivers enabled', fg='green')

    def _disable_darwin(self):
        click.secho('Revert FTDI drivers\' configuration')
        subprocess.call(['sudo', 'kextload', '-b',
                         'com.FTDI.driver.FTDIUSBSerialDriver'])
        subprocess.call(['sudo', 'kextload', '-b',
                         'com.apple.driver.AppleUSBFTDI'])
        click.secho('FPGA drivers disabled', fg='green')

    def _enable_windows(self):
        import webbrowser
        url = 'https://github.com/FPGAwars/apio/wiki/enableation#windows'
        click.secho('Follow the next instructions: ' + url)
        webbrowser.open(url)

    def _disable_windows(self):
        pass
