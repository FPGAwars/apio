# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click
import subprocess

from os.path import join, dirname, isfile, isdir

from apio import util

platform = util.get_systype()


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
                         'com.FTDI.driver.FTDIUSBSerialDriver', '-q'])
        subprocess.call(['sudo', 'kextunload', '-b',
                         'com.apple.driver.AppleUSBFTDI', '-q'])
        click.secho('FPGA drivers enabled', fg='green')

    def _disable_darwin(self):
        click.secho('Revert FTDI drivers\' configuration')
        subprocess.call(['sudo', 'kextload', '-b',
                         'com.FTDI.driver.FTDIUSBSerialDriver', '-q'])
        subprocess.call(['sudo', 'kextload', '-b',
                         'com.apple.driver.AppleUSBFTDI', '-q'])
        click.secho('FPGA drivers disabled', fg='green')

    def _enable_windows(self):
        click.secho('Launch FTDI driver configuration tool')

        result = self._run('zadig.exe')

        if isinstance(result, int):
            return result

        if result:
            return result['returncode']

    def _disable_windows(self):
        pass

    def _run(self, command):
        result = {}
        drivers_base_dir = util.get_package_dir('tools-drivers')
        drivers_bin_dir = join(drivers_base_dir, 'bin')

        if isdir(drivers_bin_dir):
            result = util.exec_command(
                join(drivers_bin_dir, command),
                stdout=util.AsyncPipe(self._on_run_out),
                stderr=util.AsyncPipe(self._on_run_out)
                )
        else:
            util._check_package('tools-drivers')
            return 1

        return result

    def _on_run_out(self, line):
        click.secho(line)
