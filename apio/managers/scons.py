# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2017 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import os
import time
import click
import datetime

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
        return self.run('-c', deps=['scons'])

    @util.command
    def verify(self):
        return self.run('verify', deps=['scons', 'iverilog'])

    @util.command
    def sim(self):
        return self.run('sim', deps=['scons', 'iverilog', 'gtkwave'])

    @util.command
    def build(self, args):
        variables, board = process_arguments(args, self.resources)
        return self.run('build', variables, board, deps=['scons', 'icestorm'])

    @util.command
    def time(self, args):
        variables, board = process_arguments(args, self.resources)
        return self.run('time', variables, board, deps=['scons', 'icestorm'])

    @util.command
    def upload(self, args, device=-1):
        variables, board = process_arguments(args, self.resources)
        device = self.get_device(board, device)
        programmer = self.get_programmer(board)
        variables += ['prog={0}'.format(programmer.replace('%D%', device))]
        return self.run('upload', variables, board, deps=['scons', 'icestorm'])

    def get_programmer(self, board):
        programmer = ''
        if board:
            p = self.resources.boards[board]['programmer']
            type = p['type']
            content = self.resources.programmers[type]
            extra_args = p['extra_args'] if 'extra_args' in p else ''
            command = content['command'] if 'command' in content else ''
            args = content['args'] if 'args' in content else ''
            programmer = '{0} {1} {2}'.format(command, args, extra_args)
        return programmer

    def get_device(self, board, device):
        check_info = self.resources.boards[board]['check']
        # Check FTDI description
        device = self._check_ftdi(check_info, device, board)
        if device == -1:
            # Board not detected
            raise Exception('board not detected')
        # Check platform
        self._check_platform(check_info, device)
        return device

    def _check_ftdi(self, check, device, board):  # noqa
        if 'ftdi-desc' in check:
            ftdi_desc = check['ftdi-desc']
            detected_boards = System().detect_boards()

            if device:
                # Check device argument
                if board:
                    found = False
                    for b in detected_boards:
                        # Selected board
                        if device == b['index']:
                            # Check the device ftdi description
                            if ftdi_desc in b['description']:
                                found = True
                            break
                    if not found:
                        device = -1
                else:
                    # Check device id
                    if int(device) >= len(detected_boards):
                        device = -1
            else:
                # Detect device
                device = -1
                if board:
                    for b in detected_boards:
                        if ftdi_desc in b['description']:
                            # Select the first board that validates
                            # the ftdi description
                            device = b['index']
                            break
                else:
                    # Insufficient arguments
                    click.secho(
                        'Error: insufficient arguments: device or board',
                        fg='red')
                    click.secho(
                        'You have two options:\n' +
                        '  1) Execute your command with\n' +
                        '       `--device <deviceid>`\n' +
                        '  2) Execute your command with\n' +
                        '       `--board <boardname>`',
                        fg='yellow')
        return device

    def _check_platform(self, check, device):
        if 'platform' in check:
            # Device argument is ignored
            if device and device != -1:
                click.secho(
                    'Info: ignore device argument {0}'.format(device),
                    fg='yellow')

            platform = check['platform']
            current_platform = util.get_systype()
            if platform != current_platform:
                # Incorrect platform
                if platform == 'linux_armv7l':
                    raise Exception(
                        'incorrect platform: RPI2 or RPI3 required')
                else:
                    raise Exception(
                        'incorrect platform {0}'.format(platform))

    def run(self, command, variables=[], board=None, deps=[]):
        """Executes scons for building"""

        # -- Check for the SConstruct file
        if not isfile(util.safe_join(util.get_project_dir(), 'SConstruct')):
            click.secho('Info: default SConstruct file')
            variables += ['-f']
            variables += [util.safe_join(
                util.get_folder('resources'), 'SConstruct')]

        # -- Resolve packages
        if self.profile.check_exe_default():
            # Run on `default` config mode
            if not util.resolve_packages(self.resources.packages, deps):
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
            stdout=util.AsyncPipe(self._on_run_out),
            stderr=util.AsyncPipe(self._on_run_err)
        )

        # -- Print result
        exit_code = result['returncode']
        is_error = exit_code != 0
        summary_text = ' Took %.2f seconds ' % (time.time() - start_time)
        half_line = '=' * int(
            ((terminal_width - len(summary_text) - 10) / 2))
        click.echo('%s [%s]%s%s' % (
            half_line,
            (click.style(' ERROR ', fg='red', bold=True)
             if is_error else click.style('SUCCESS', fg='green',
                                          bold=True)),
            summary_text,
            half_line
        ), err=is_error)

        return exit_code

    def _on_run_out(self, line):
        fg = 'green' if 'is up to date' in line else None
        click.secho(line, fg=fg)

    def _on_run_err(self, line):
        time.sleep(0.01)  # Delay
        fg = 'red' if 'error' in line.lower() else 'yellow'
        click.secho(line, fg=fg)
