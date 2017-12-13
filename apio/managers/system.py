# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2017 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import re
import click
import platform

from os.path import isdir

from apio import util


class System(object):  # pragma: no cover
    def __init__(self):
        self.ext = ''
        if 'Windows' == platform.system():
            self.ext = '.exe'

    def lsusb(self):
        returncode = 1
        result = self._run_command('lsusb')

        if result:
            returncode = result.get('returncode')

        return returncode

    def lsftdi(self):
        returncode = 1
        result = self._run_command('lsftdi')

        if result:
            returncode = result.get('returncode')

        return returncode

    def lsserial(self):
        returncode = 0
        serial_ports = util.get_serial_ports()
        click.secho(
            'Number of Serial devices found: {}\n'.format(len(serial_ports)))

        for serial_port in serial_ports:
            port = serial_port.get('port')
            description = serial_port.get('description')
            hwid = serial_port.get('hwid')
            click.secho(port, fg='cyan')
            click.secho('Description: {}'.format(description))
            click.secho('Hardware info: {}\n'.format(hwid))

        return returncode

    def get_ftdi_devices(self):
        ftdi_devices = []
        result = self._run_command('lsftdi')

        if result and result.get('returncode') == 0:
            ftdi_devices = self._parse_ftdi_devices(result.get('out'))
        else:
            raise Exception

        return ftdi_devices

    def _run_command(self, command):
        result = {}
        system_base_dir = util.get_package_dir('tools-system')
        system_bin_dir = util.safe_join(system_base_dir, 'bin')

        if isdir(system_bin_dir):
            result = util.exec_command(
                util.safe_join(system_bin_dir, command + self.ext),
                stdout=util.AsyncPipe(self._on_run_out),
                stderr=util.AsyncPipe(self._on_run_out))
        else:
            util._check_package('system')

        return result

    def _on_run_out(self, line):
        click.secho(line)

    def _parse_ftdi_devices(self, text):
        pattern = 'Number\sof\sFTDI\sdevices\sfound:\s(?P<n>\d+?)\n'
        match = re.search(pattern, text)
        n = int(match.group('n')) if match else 0

        pattern = '.*Checking\sdevice:\s(?P<index>.*?)\n.*'
        index = re.findall(pattern, text)

        pattern = '.*Manufacturer:\s(?P<n>.*?),.*'
        manufacturer = re.findall(pattern, text)

        pattern = '.*Description:\s(?P<n>.*?)\n.*'
        description = re.findall(pattern, text)

        ftdi_devices = []

        for i in range(n):
            ftdi_device = {
                'index': index[i],
                'manufacturer': manufacturer[i],
                'description': description[i]
            }
            ftdi_devices.append(ftdi_device)

        return ftdi_devices
