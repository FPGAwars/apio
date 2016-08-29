# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import re
import click
import platform

from os.path import join, isdir

from apio import util


class System(object):  # pragma: no cover
    def __init__(self):
        self.ext = ''
        if 'Windows' == platform.system():
            self.ext = '.exe'

    def lsusb(self):
        result = self._run('listdevs')

        if isinstance(result, int):
            return result

        if result:
            return result['returncode']

    def lsftdi(self):
        result = self._run('find_all')

        if isinstance(result, int):
            return result

        if result:
            return result['returncode']

    def detect_boards(self):
        detected_boards = []
        result = self._run('find_all')

        if isinstance(result, int):
            return result

        if result and result['returncode'] == 0:
            detected_boards = self.parse_out(result['out'])

        return detected_boards

    def _run(self, command):
        result = {}
        system_dir = join(util.get_home_dir(), 'packages', 'system')

        if isdir(system_dir):
            result = util.exec_command(
                join(system_dir, command + self.ext),
                stdout=util.AsyncPipe(self._on_run_out),
                stderr=util.AsyncPipe(self._on_run_out)
                )
        else:
            click.secho('Error: system tools are not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install system', fg='yellow')
            return 1

        return result

    def _on_run_out(self, line):
        click.secho(line)

    def parse_out(self, text):
        pattern = 'Number\sof\sFTDI\sdevices\sfound:\s(?P<n>\d+?)\n'
        match = re.search(pattern, text)
        n = int(match.group('n')) if match else 0

        pattern = '.*Checking\sdevice:\s(?P<index>.*?)\n.*'
        index = re.findall(pattern, text)

        pattern = '.*Manufacturer:\s(?P<n>.*?),.*'
        manufacturer = re.findall(pattern, text)

        pattern = '.*Description:\s(?P<n>.*?)\n.*'
        description = re.findall(pattern, text)

        detected_boards = []

        for i in range(n):
            board = {
                "index": index[i],
                "manufacturer": manufacturer[i],
                "description": description[i]
            }
            detected_boards.append(board)

        return detected_boards
