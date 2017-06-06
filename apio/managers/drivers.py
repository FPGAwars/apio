# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2017 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import os
import click
import subprocess

from os.path import isfile, isdir

from apio import util
from apio.profile import Profile

platform = util.get_systype()

FTDI_INSTALL_DRIVER_INSTRUCTIONS = """
   FTDI driver installation:
   Usage instructions

      1. Connect the FTDI FPGA board
      2. Select (Interface 0)
      3. Replace driver by "libusbK"
      4. Reconnect the board
      5. Check `apio system --lsftdi`
"""

FTDI_UNINSTALL_DRIVER_INSTRUCTIONS = """
   FTDI driver uninstallation:
   Usage instructions

      1. Find the FPGA USB Devices
      2. Right click
      3. Select "Uninstall"
      4. Accept the dialog"""


class Drivers(object):  # pragma: no cover

    rules_local_path = util.safe_join(
        util.get_folder('resources'), '80-icestick.rules')
    rules_system_path = '/etc/udev/rules.d/80-icestick.rules'

    # Driver to restore: mac os
    driverC = ''

    def enable(self):
        if 'linux' in platform:
            return self._enable_linux()
        elif 'darwin' in platform:
            self.profile = Profile()
            return self._enable_darwin()
        elif 'windows' in platform:
            return self._enable_windows()

    def disable(self):
        if 'linux' in platform:
            return self._disable_linux()
        elif 'darwin' in platform:
            self.profile = Profile()
            return self._disable_darwin()
        elif 'windows' in platform:
            return self._disable_windows()

    def pre_upload(self):
        if 'darwin' in platform:
            self.profile = Profile()
            self._pre_upload_darwin()

    def post_upload(self):
        if 'darwin' in platform:
            self.profile = Profile()
            self._post_upload_darwin()

    def _enable_linux(self):
        click.secho('Configure FTDI drivers for FPGA')
        if not isfile(self.rules_system_path):
            subprocess.call(['sudo', 'cp',
                             self.rules_local_path, self.rules_system_path])
            subprocess.call(['sudo', 'service', 'udev', 'restart'])
            # subprocess.call(['sudo', 'udevadm', 'control', '--reload-rules'])
            # subprocess.call(['sudo', 'udevadm', 'trigger'])
            click.secho('FPGA drivers enabled', fg='green')
            click.secho('Unplug and reconnect your board', fg='yellow')
        else:
            click.secho('Already enabled', fg='yellow')

    def _disable_linux(self):
        if isfile(self.rules_system_path):
            click.secho('Revert FTDI drivers\' configuration')
            subprocess.call(['sudo', 'rm', self.rules_system_path])
            subprocess.call(['sudo', 'service', 'udev', 'restart'])
            # subprocess.call(['sudo', 'udevadm', 'control', '--reload-rules'])
            # subprocess.call(['sudo', 'udevadm', 'trigger'])
            click.secho('FPGA drivers disabled', fg='green')
            click.secho('Unplug and reconnect your board', fg='yellow')
        else:
            click.secho('Already disabled', fg='yellow')

    def _enable_darwin(self):
        # Check homebrew
        brew = subprocess.call('which brew > /dev/null', shell=True)
        if brew != 0:
            click.secho('Error: homebrew is required', fg='red')
        else:
            click.secho('Enable FTDI drivers for FPGA')
            subprocess.call(['brew', 'update'])
            subprocess.call(['brew', 'install', '--force', 'libftdi'])
            subprocess.call(['brew', 'unlink', 'libftdi'])
            subprocess.call(['brew', 'link', '--force', 'libftdi'])
            subprocess.call(['brew', 'install', '--force', 'libffi'])
            subprocess.call(['brew', 'unlink', 'libffi'])
            subprocess.call(['brew', 'link', '--force', 'libffi'])
            self.profile.add_setting('macos_drivers', True)
            self.profile.save()
            click.secho('FPGA drivers enabled', fg='green')

    def _disable_darwin(self):
        click.secho('Disable FTDI drivers\' configuration')
        self.profile.add_setting('macos_drivers', False)
        self.profile.save()
        click.secho('FPGA drivers disabled', fg='green')

    def _pre_upload_darwin(self):
        if self.profile.settings.get('macos_drivers', False):
            # Check and unload the drivers
            driverA = 'com.FTDI.driver.FTDIUSBSerialDriver'
            driverB = 'com.apple.driver.AppleUSBFTDI'
            if self._check_driver_darwin(driverA):
                subprocess.call(['sudo', 'kextunload', '-b', driverA])
                self.driverC = driverA
            elif self._check_driver_darwin(driverB):
                subprocess.call(['sudo', 'kextunload', '-b', driverB])
                self.driverC = driverB

    def _post_upload_darwin(self):
        if self.profile.settings.get('macos_drivers', False):
            # Restore previous driver configuration
            if self.driverC:
                subprocess.call(['sudo', 'kextload', '-b', self.driverC])

    def _check_driver_darwin(self, driver):
        return driver in subprocess.check_output(['kextstat'])

    def _enable_windows(self):
        drivers_base_dir = util.get_package_dir('tools-drivers')
        drivers_bin_dir = util.safe_join(drivers_base_dir, 'bin')
        drivers_share_dir = util.safe_join(drivers_base_dir, 'share')
        zadig_ini_path = util.safe_join(drivers_share_dir, 'zadig.ini')
        zadig_ini = 'zadig.ini'

        try:
            if isdir(drivers_bin_dir):
                click.secho('Launch drivers configuration tool')
                click.secho(FTDI_INSTALL_DRIVER_INSTRUCTIONS, fg='yellow')
                # Copy zadig.ini
                with open(zadig_ini, 'w') as ini_file:
                    with open(zadig_ini_path, 'r') as local_ini_file:
                        ini_file.write(local_ini_file.read())

                result = util.exec_command(
                    util.safe_join(drivers_bin_dir, 'zadig.exe'))
                click.secho('FPGA drivers configuration finished', fg='green')
            else:
                util._check_package('drivers')
                result = 1
        except Exception as e:
            click.secho('Error: ' + str(e), fg='red')
            result = 1
        finally:
            # Remove zadig.ini
            if isfile(zadig_ini):
                os.remove(zadig_ini)

        if not isinstance(result, int):
            result = result['returncode']
        return result

    def _disable_windows(self):
        click.secho('Launch device manager')
        click.secho(FTDI_UNINSTALL_DRIVER_INSTRUCTIONS, fg='yellow')

        result = util.exec_command('mmc devmgmt.msc')
        return result['returncode']
