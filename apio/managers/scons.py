# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import os
import sys
import time
import click
import datetime

from os.path import join, dirname, isdir, isfile

from apio import util
from apio.resources import Resources
from apio.managers.system import System
from apio.managers.project import Project


class SCons(object):

    def __init__(self):
        self.resources = Resources()

    def clean(self):
        return self.run('-c')

    def verify(self):
        return self.run('verify')

    def sim(self):
        return self.run('sim')

    def build(self, args):
        ret = self.process_arguments(args)
        if isinstance(ret, int):
            return ret
        if isinstance(ret, tuple):
            variables, board = ret
        return self.run('build', variables, board)

    def upload(self, args, device=-1):
        ret = self.process_arguments(args)
        if isinstance(ret, int):
            return ret
        if isinstance(ret, tuple):
            variables, board = ret

        # Get programmer value
        if board:
            p = self.resources.boards[board]['programmer']
            programmer = p['type']
            programmer_args = p['args'] if 'args' in p else ''
        else:
            programmer = 'iceprog'
            programmer_args = ''

        # -- Check
        check = self.resources.boards[board]['check']

        # Check FTDI description
        if 'ftdi-desc' in check:
            detected_boards = System().detect_boards()
            if isinstance(detected_boards, int):
                return detected_boards

            if device:
                # Check device argument
                if board:
                    desc = check['ftdi-desc']
                    check = False
                    for b in detected_boards:
                        # Selected board
                        if device == b['index']:
                            # Check the device ftdi description
                            if desc in b['description']:
                                check = True
                            break
                    if not check:
                        device = -1
                else:
                    # Check device id
                    if int(device) >= len(detected_boards):
                        device = -1
            else:
                # Detect device
                device = -1
                if board:
                    desc = check['ftdi-desc']
                    for b in detected_boards:
                        if desc in b['description']:
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
                    return 1

            if device == -1:
                # Board not detected
                click.secho('Error: board not detected', fg='red')
                return 1

        # Check architectures
        if 'arch' in check:
            # Device argument is ignored
            if device and device != -1:
                click.secho(
                    'Info: ignore device argument {0}'.format(device),
                    fg='yellow')

            arch = check['arch']
            current_arch = util.get_systype()
            if arch != current_arch:
                # Incorrect architecture
                if arch == 'linux_armv7l':
                    click.secho(
                        'Error: incorrect architecture: RPI2 or RPI3 required',
                        fg='red')
                else:
                    click.secho(
                        'Error: incorrect architecture {0}'.format(arch),
                        fg='red')
                return 1

        return self.run('upload',
                        variables + ['device={0}'.format(device),
                                     'prog={0}'.format(programmer),
                                     'prog_args={0}'.format(programmer_args)],
                        board)

    def time(self, args):
        ret = self.process_arguments(args)
        if isinstance(ret, int):
            return ret
        if isinstance(ret, tuple):
            variables, board = ret
        return self.run('time', variables, board)

    def run(self, command, variables=[], board=None):
        """Executes scons for building"""

        packages_dir = os.path.join(util.get_home_dir(), 'packages')
        icestorm_dir = os.path.join(packages_dir, 'toolchain-icestorm', 'bin')
        iverilog_dir = os.path.join(packages_dir, 'toolchain-iverilog', 'bin')
        scons_dir = os.path.join(packages_dir, 'tool-scons', 'script')
        sconstruct_name = 'SConstruct'

        # Give the priority to the packages installed by apio
        os.environ['PATH'] = os.pathsep.join(
            [iverilog_dir, icestorm_dir, os.environ['PATH']])

        # Add environment variables
        os.environ['IVL'] = os.path.join(
            packages_dir, 'toolchain-iverilog', 'lib', 'ivl')
        os.environ['VLIB'] = os.path.join(
            packages_dir, 'toolchain-iverilog', 'vlib', 'system.v')

        # -- Check for the SConstruct file
        if not isfile(join(util.get_project_dir(), sconstruct_name)):
            click.secho('Using default SConstruct file')
            variables += ['-f', join(
                dirname(__file__), '..', 'resources', sconstruct_name)]

        # -- Check for the scons tools
        if not isdir(scons_dir):
            click.secho('Error: scons toolchain is not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install scons', fg='yellow')

        # -- Check for the icestorm tools
        if not isdir(icestorm_dir):
            click.secho('Error: icestorm toolchain is not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install icestorm', fg='yellow')

        # -- Check for the iverilog tools
        if not isdir(iverilog_dir):
            click.secho('Error: iverilog toolchain is not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install iverilog', fg='yellow')

        # -- Execute scons
        if isdir(scons_dir) and isdir(icestorm_dir) and isdir(iverilog_dir):
            terminal_width, _ = click.get_terminal_size()
            start_time = time.time()

            if command == 'build' or \
               command == 'upload' or \
               command == 'time':
                if board:
                    processing_board = board
                else:
                    processing_board = 'custom board'
                click.echo("[%s] Processing %s" % (
                    datetime.datetime.now().strftime("%c"),
                    click.style(processing_board, fg="cyan", bold=True)))
                click.secho("-" * terminal_width, bold=True)

            click.secho("Executing: scons -Q {0} {1}".format(
                            command, ' '.join(variables)))
            result = util.exec_command(
                [
                    os.path.normpath(sys.executable),
                    os.path.join(scons_dir, 'scons'),
                    '-Q',
                    command
                ] + variables,
                stdout=util.AsyncPipe(self._on_run_out),
                stderr=util.AsyncPipe(self._on_run_err)
            )

            # -- Print result
            exit_code = result['returncode']
            is_error = exit_code != 0
            summary_text = " Took %.2f seconds " % (time.time() - start_time)
            half_line = "=" * int(
                ((terminal_width - len(summary_text) - 10) / 2))
            click.echo("%s [%s]%s%s" % (
                half_line,
                (click.style(" ERROR ", fg="red", bold=True)
                 if is_error else click.style("SUCCESS", fg="green",
                                              bold=True)),
                summary_text,
                half_line
            ), err=is_error)

            if False:
                if is_error:
                    print("""
  ______                     _
 |  ____|                   | |
 | |__   _ __ _ __ ___  _ __| |
 |  __| | '__| '__/ _ \| '__| |
 | |____| |  | | | (_) | |  |_|
 |______|_|  |_|  \___/|_|  (_)
""")
                else:
                    print("""
   _____                             _
  / ____|                           | |
 | (___  _   _  ___ ___ ___  ___ ___| |
  \___ \| | | |/ __/ __/ _ \/ __/ __| |
  ____) | |_| | (_| (_|  __/\__ \__ \_|
 |_____/ \__,_|\___\___\___||___/___(_)
""")

            return exit_code
        else:
            return 1

    def process_arguments(self, args):
        # -- Check arguments
        var_board = args['board']
        var_fpga = args['fpga']
        var_size = args['size']
        var_type = args['type']
        var_pack = args['pack']

        # TODO: reduce code size

        if var_board:
            if isfile('apio.ini'):
                click.secho('Info: ignore apio.ini board', fg='yellow')
            if var_board in self.resources.boards:
                fpga = self.resources.boards[var_board]['fpga']
                if fpga in self.resources.fpgas:
                    fpga_size = self.resources.fpgas[fpga]['size']
                    fpga_type = self.resources.fpgas[fpga]['type']
                    fpga_pack = self.resources.fpgas[fpga]['pack']

                    redundant_arguments = []
                    contradictory_arguments = []

                    if var_fpga:
                        if var_fpga in self.resources.fpgas:
                            if var_fpga == fpga:
                                # Redundant argument
                                redundant_arguments += ['fpga']
                            else:
                                # Contradictory argument
                                contradictory_arguments += ['fpga']
                        else:
                            # Unknown fpga
                            click.secho(
                                'Error: unknown fpga: {0}'.format(
                                    var_fpga), fg='red')
                            return 1

                    if var_size:
                        if var_size == fpga_size:
                            # Redundant argument
                            redundant_arguments += ['size']
                        else:
                            # Contradictory argument
                            contradictory_arguments += ['size']

                    if var_type:
                        if var_type == fpga_type:
                            # Redundant argument
                            redundant_arguments += ['type']
                        else:
                            # Contradictory argument
                            contradictory_arguments += ['type']

                    if var_pack:
                        if var_pack == fpga_pack:
                            # Redundant argument
                            redundant_arguments += ['pack']
                        else:
                            # Contradictory argument
                            contradictory_arguments += ['pack']

                    if redundant_arguments:
                        # Redundant argument
                        click.secho(
                            'Warning: redundant arguments: {}'.format(
                                ', '.join(redundant_arguments)), fg='yellow')

                    if contradictory_arguments:
                        # Contradictory argument
                        click.secho(
                            'Error: contradictory arguments: {}'.format(
                                ', '.join(contradictory_arguments)), fg='red')
                        return 1
                else:
                    # Unknown fpga
                    pass
            else:
                # Unknown board
                click.secho(
                    'Error: unknown board: {0}'.format(var_board), fg='red')
                return 1
        else:
            if var_fpga:
                if isfile('apio.ini'):
                    click.secho('Info: ignore apio.ini board', fg='yellow')
                if var_fpga in self.resources.fpgas:
                    fpga_size = self.resources.fpgas[var_fpga]['size']
                    fpga_type = self.resources.fpgas[var_fpga]['type']
                    fpga_pack = self.resources.fpgas[var_fpga]['pack']

                    redundant_arguments = []
                    contradictory_arguments = []

                    if var_size:
                        if var_size == fpga_size:
                            # Redundant argument
                            redundant_arguments += ['size']
                        else:
                            # Contradictory argument
                            contradictory_arguments += ['size']

                    if var_type:
                        if var_type == fpga_type:
                            # Redundant argument
                            redundant_arguments += ['type']
                        else:
                            # Contradictory argument
                            contradictory_arguments += ['type']

                    if var_pack:
                        if var_pack == fpga_pack:
                            # Redundant argument
                            redundant_arguments += ['pack']
                        else:
                            # Contradictory argument
                            contradictory_arguments += ['pack']

                    if redundant_arguments:
                        # Redundant argument
                        click.secho(
                            'Warning: redundant arguments: {}'.format(
                                ', '.join(redundant_arguments)), fg='yellow')

                    if contradictory_arguments:
                        # Contradictory argument
                        click.secho(
                            'Error: contradictory arguments: {}'.format(
                                ', '.join(contradictory_arguments)), fg='red')
                        return 1
                else:
                    # Unknown fpga
                    click.secho(
                        'Error: unknown fpga: {0}'.format(var_fpga), fg='red')
                    return 1
            else:
                if var_size and var_type and var_pack:
                    if isfile('apio.ini'):
                        click.secho('Info: ignore apio.ini board', fg='yellow')
                    fpga_size = var_size
                    fpga_type = var_type
                    fpga_pack = var_pack
                else:
                    if not var_size and not var_type and not var_pack:
                        # No arguments: use apio.ini board
                        p = Project()
                        p.read()
                        if p.board:
                            var_board = p.board
                            click.secho(
                                'Info: use apio.ini board: {}'.format(
                                    var_board))
                            fpga = self.resources.boards[var_board]['fpga']
                            fpga_size = self.resources.fpgas[fpga]['size']
                            fpga_type = self.resources.fpgas[fpga]['type']
                            fpga_pack = self.resources.fpgas[fpga]['pack']
                        else:
                            click.secho(
                                'Error: insufficient arguments: missing board',
                                fg='red')
                            click.secho(
                                'You have two options:\n' +
                                '  1) Execute your command with\n' +
                                '       `--board <boardname>`\n' +
                                '  2) Create an ini file using\n' +
                                '       `apio init --board <boardname>`',
                                fg='yellow')
                            return 1
                    else:
                        if isfile('apio.ini'):
                            click.secho('Info: ignore apio.ini board',
                                        fg='yellow')
                        # Insufficient arguments
                        missing = []
                        if not var_size:
                            missing += ['size']
                        if not var_type:
                            missing += ['type']
                        if not var_pack:
                            missing += ['pack']
                        pass
                        click.secho(
                            'Error: insufficient arguments: missing {}'.format(
                                ', '.join(missing)), fg='red')
                        return 1

        # -- Build Scons variables list
        variables = self.format_vars({
            "fpga_size": fpga_size,
            "fpga_type": fpga_type,
            "fpga_pack": fpga_pack
        })

        return variables, var_board

    def format_vars(self, args):
        """Format the given vars in the form: 'flag=value'"""
        variables = []
        for key, value in args.items():
            if value:
                variables += ["{0}={1}".format(key, value)]
        return variables

    def _on_run_out(self, line):
        fg = 'green' if 'is up to date' in line else None
        click.secho(line, fg=fg)

    def _on_run_err(self, line):
        time.sleep(0.01)  # Delay
        fg = 'red' if 'error' in line.lower() else 'yellow'
        click.secho(line, fg=fg)
