# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import os
import re
import time
import click
import datetime
import pkg_resources
import semantic_version

from os.path import isfile

from apio import util
from apio.managers.arguments import process_arguments
from apio.managers.system import System
from apio.profile import Profile
from apio.resources import Resources


class SCons(object):

    def __init__(self, project_dir=''):
        self.resources = Resources()
        self.profile = Profile()

        if project_dir is not None:
            # Move to project dir
            project_dir = util.check_dir(project_dir)
            os.chdir(project_dir)

    @util.command
    def clean(self):
        return self.run('-c', packages=['scons'])

    @util.command
    def verify(self):
        return self.run('verify', packages=['scons', 'iverilog'])

    @util.command
    def sim(self):
        return self.run('sim', packages=['scons', 'iverilog', 'gtkwave'])

    @util.command
    def build(self, args):
        var, board = process_arguments(args, self.resources)
        return self.run('build', var, board, packages=['scons', 'icestorm'])

    @util.command
    def time(self, args):
        var, board = process_arguments(args, self.resources)
        return self.run('time', var, board, packages=['scons', 'icestorm'])

    @util.command
    def upload(self, args, serial_port, ftdi_id, sram):
        var, board = process_arguments(args, self.resources)
        programmer = self.get_programmer(board, serial_port, ftdi_id, sram)
        var += ['prog={0}'.format(programmer)]
        return self.run('upload', var, board, packages=['scons', 'icestorm'])

    def get_programmer(self, board, ext_serial_port, ext_ftdi_id, sram):
        programmer = ''

        if board:
            board_data = self.resources.boards.get(board)

            # Check platform
            self.check_platform(board_data)

            # Check pip packages
            self.check_pip_packages(board_data)

            # Serialize programmer command
            programmer = self.serialize_programmer(board_data, sram)

            # Replace USB vendor id
            if '${VID}' in programmer:
                vid = board_data.get('usb').get('vid')
                programmer = programmer.replace('${VID}', vid)

            # Replace USB product id
            if '${PID}' in programmer:
                pid = board_data.get('usb').get('pid')
                programmer = programmer.replace('${PID}', pid)

            # Replace FTDI index
            if '${FTDI_ID}' in programmer:
                self.check_usb(board_data)
                ftdi_id = self.get_ftdi_id(board_data, ext_ftdi_id)
                programmer = programmer.replace('${FTDI_ID}', ftdi_id)

            # Replace Serial port
            if '${SERIAL_PORT}' in programmer:
                self.check_usb(board_data)
                device = self.get_serial_port(board_data, ext_serial_port)
                programmer = programmer.replace('${SERIAL_PORT}', device)

        return programmer

    def check_platform(self, board_data):
        if 'platform' not in board_data:
            return

        platform = board_data.get('platform')
        current_platform = util.get_systype()
        if platform != current_platform:
            # Incorrect platform
            if platform == 'linux_armv7l':
                raise Exception(
                    'incorrect platform: RPI2 or RPI3 required')
            else:
                raise Exception(
                    'incorrect platform {0}'.format(platform))

    def check_pip_packages(self, board_data):
        prog_info = board_data.get('programmer')
        content = self.resources.programmers.get(prog_info.get('type'))
        all_pip_packages = self.resources.distribution.get('pip_packages')

        pip_packages = content.get('pip_packages') or []
        for pip_pkg in pip_packages:
            try:
                # Check pip_package version
                spec = semantic_version.Spec(all_pip_packages.get(pip_pkg, ''))
                pkg_version = pkg_resources.get_distribution(pip_pkg).version
                version = semantic_version.Version(pkg_version)
                if not spec.match(version):
                    click.secho(
                        'Error: \'{}\' '.format(pip_pkg) +
                        'version ({}) '.format(version) +
                        'does not match {}'.format(spec),
                        fg='red')
                    click.secho('Please run:\n'
                                '   pip install -U apio[{}]'.format(pip_pkg),
                                fg='yellow')
                    raise Exception
            except pkg_resources.DistributionNotFound:
                click.secho(
                    'Error: {} is not installed'.format(pip_pkg),
                    fg='red')
                click.secho('Please run:\n'
                            '   pip install -U apio[{}]'.format(pip_pkg),
                            fg='yellow')
                raise Exception
            try:
                # Check pip_package itself
                __import__(pip_pkg)
            except Exception as e:
                # Exit if a package is not working
                python_version = util.get_python_version()
                message = '`{}` not compatible with '.format(pip_pkg)
                message += 'Python {}'.format(python_version)
                message += '\n       {}'.format(e)
                raise Exception(message)

    def serialize_programmer(self, board_data, sram):
        prog_info = board_data.get('programmer')
        content = self.resources.programmers.get(prog_info.get('type'))

        programmer = content.get('command')

        # Add args
        if content.get('args'):
            programmer += ' {}'.format(content.get('args'))

        # Add extra args
        if prog_info.get('extra_args'):
            programmer += ' {}'.format(prog_info.get('extra_args'))

        # Enable SRAM programming
        if sram:
            # Only for iceprog programmer
            if programmer.startswith('iceprog'):
                programmer += ' -S'

        return programmer

    def check_usb(self, board_data):
        if 'usb' not in board_data:
            raise Exception('Missing board configuration: usb')

        usb_data = board_data.get('usb')
        hwid = '{0}:{1}'.format(
            usb_data.get('vid'),
            usb_data.get('pid')
        )
        found = False
        for usb_device in System().get_usb_devices():
            if usb_device.get('hwid') == hwid:
                found = True
                break

        if not found:
            # Board not connected
            raise Exception('board not connected')

    def get_serial_port(self, board_data, ext_serial_port):
        # Search Serial port by USB id
        device = self._check_serial(board_data, ext_serial_port)
        if device is None:
            # Board not available
            raise Exception('board not available')
        return device

    def _check_serial(self, board_data, ext_serial_port):
        if 'usb' not in board_data:
            raise Exception('Missing board configuration: usb')

        usb_data = board_data.get('usb')
        desc_pattern = '^' + (usb_data.get('desc') or '.*') + '$'
        hwid = '{0}:{1}'.format(
            usb_data.get('vid'),
            usb_data.get('pid')
        )

        # Match the discovered serial ports
        for serial_port_data in util.get_serial_ports():
            port = serial_port_data.get('port')
            if ext_serial_port and ext_serial_port != port:
                # If the --device options is set but it doesn't match
                # with the detected port, skip the port.
                continue
            if hwid in serial_port_data.get('hwid') and \
               re.match(desc_pattern, serial_port_data.get('description')):
                # If the hwid and the description pattern matches
                # return the device for the port.
                return port

    def get_ftdi_id(self, board_data, ext_ftdi_id):
        # Search device by FTDI id
        ftdi_id = self._check_ftdi(board_data, ext_ftdi_id)
        if ftdi_id is None:
            # Board not available
            raise Exception('board not available')
        return ftdi_id

    def _check_ftdi(self, board_data, ext_ftdi_id):
        if 'ftdi' not in board_data:
            raise Exception('Missing board configuration: ftdi')

        ftdi_data = board_data.get('ftdi')
        desc_pattern = '^' + ftdi_data.get('desc') + '$'

        # Match the discovered FTDI chips
        for ftdi_device in System().get_ftdi_devices():
            index = ftdi_device.get('index')
            if ext_ftdi_id and ext_ftdi_id != index:
                # If the --device options is set but it doesn't match
                # with the detected index, skip the port.
                continue
            if re.match(desc_pattern, ftdi_device.get('description')):
                # If matches the description pattern
                # return the index for the FTDI device.
                return index

    def run(self, command, variables=[], board=None, packages=[]):
        """Executes scons for building"""

        # -- Check for the SConstruct file
        if not isfile(util.safe_join(util.get_project_dir(), 'SConstruct')):
            variables += ['-f']
            variables += [util.safe_join(
                util.get_folder('resources'), 'SConstruct')]
        else:
            click.secho('Info: use custom SConstruct file')

        # -- Resolve packages
        if self.profile.check_exe_default():
            # Run on `default` config mode
            if not util.resolve_packages(self.resources.packages, packages):
                # Exit if a package is not installed
                raise Exception
        else:
            click.secho('Info: native config mode')

        # -- Execute scons
        return self._execute_scons(command, variables, board)

    def _execute_scons(self, command, variables, board):
        terminal_width, _ = click.get_terminal_size()
        start_time = time.time()

        if command == 'build' or \
           command == 'upload' or \
           command == 'time':
            if board:
                processing_board = board
            else:
                processing_board = 'custom board'
            click.echo('[%s] Processing %s' % (
                datetime.datetime.now().strftime('%c'),
                click.style(processing_board, fg='cyan', bold=True)))
            click.secho('-' * terminal_width, bold=True)

        if self.profile.get_verbose_mode() > 0:
            click.secho('Executing: scons -Q {0} {1}'.format(
                            command, ' '.join(variables)))

        result = util.exec_command(
            util.scons_command + ['-Q', command] + variables,
            stdout=util.AsyncPipe(self._on_stdout),
            stderr=util.AsyncPipe(self._on_stderr)
        )

        # -- Print result
        exit_code = result.get('returncode')
        is_error = exit_code != 0
        summary_text = ' Took %.2f seconds ' % (time.time() - start_time)
        half_line = '=' * int(
            ((terminal_width - len(summary_text) - 10) / 2))
        click.echo('%s [%s]%s%s' % (
            half_line,
            (click.style(' ERROR ', fg='red', bold=True)
             if is_error else click.style('SUCCESS', fg='green', bold=True)),
            summary_text,
            half_line
        ), err=is_error)

        return exit_code

    def _on_stdout(self, line):
        fg = 'green' if 'is up to date' in line else None
        click.secho(line, fg=fg)

    def _on_stderr(self, line):
        time.sleep(0.01)  # Delay
        fg = 'red' if 'error' in line.lower() else 'yellow'
        click.secho(line, fg=fg)
