# Execute functions

import os
import sys
import time
import click
import platform
import datetime

from os.path import join, dirname, isdir, isfile, expanduser
from .project import Project

from . import util

try:
    input = raw_input
except NameError:
    pass


class System(object):
    def __init__(self):
        self.ext = ''
        if 'Windows' == platform.system():
            self.ext = '.exe'

    def lsusb(self):
        self._run('listdevs')

    def lsftdi(self):
        self._run('find_all')

    def _run(self, command):
        system_dir = join(expanduser('~'), '.apio', 'system')
        tools_usb_ftdi_dir = join(system_dir, 'tools-usb-ftdi')

        if isdir(tools_usb_ftdi_dir):
            util.exec_command(
                os.path.join(tools_usb_ftdi_dir, command + self.ext),
                stdout=util.AsyncPipe(self._on_run_out),
                stderr=util.AsyncPipe(self._on_run_out)
            )
        else:
            click.secho('Error: system tools are not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install system', fg='yellow')

    def _on_run_out(self, line):
        click.secho(line)


class SCons(object):

    def run(self, variables=[]):
        """Executes scons for building"""

        packages_dir = os.path.join(util.get_home_dir(), 'packages')
        icestorm_dir = os.path.join(packages_dir, 'toolchain-icestorm', 'bin')
        scons_dir = os.path.join(packages_dir, 'tool-scons', 'script')
        sconstruct_name = 'SConstruct'

        # Give the priority to the packages installed by apio
        os.environ['PATH'] = os.pathsep.join(
            [icestorm_dir, os.environ['PATH']])

        # -- Check for the icestorm tools
        if not isdir(icestorm_dir):
            click.secho('Error: icestorm toolchain is not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install icestorm', fg='yellow')

        # -- Check for the scons
        if not isdir(scons_dir):
            click.secho('Error: scons toolchain is not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install scons', fg='yellow')

        # -- Check for the SConstruct file
        if not isfile(join(os.getcwd(), sconstruct_name)):
            click.secho('Using default SConstruct file', fg='yellow')
            variables += ['-f', join(dirname(__file__), sconstruct_name)]

        # -- Check for the project configuration file
        p = Project()
        p.read()
        board_flag = "board={}".format(p.board)
        variables.append(board_flag)

        # -- Execute scons
        if isdir(scons_dir) and isdir(icestorm_dir):
            terminal_width, _ = click.get_terminal_size()
            start_time = time.time()

            click.echo("[%s] Processing %s" % (
                datetime.datetime.now().strftime("%c"),
                click.style(p.board, fg="cyan", bold=True)))
            click.secho("-" * terminal_width, bold=True)

            click.secho("Executing: scons -Q {}".format(' '.join(variables)))
            result = util.exec_command(
                [
                    os.path.normpath(sys.executable),
                    os.path.join(scons_dir, 'scons'),
                    '-Q'
                ] + variables,
                stdout=util.AsyncPipe(self._on_run_out),
                stderr=util.AsyncPipe(self._on_run_err)
            )

            # -- Print result
            exit_code = result['returncode']
            is_error = exit_code != 0
            summary_text = " Took %.2f seconds " % (time.time() - start_time)
            half_line = "=" * int(((terminal_width - len(summary_text) - 10) / 2))
            click.echo("%s [%s]%s%s" % (
                half_line,
                (click.style(" ERROR ", fg="red", bold=True)
                 if is_error else click.style("SUCCESS", fg="green",
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

    def create_sconstruct(self):
        sconstruct_name = 'SConstruct'
        sconstruct_path = join(os.getcwd(), sconstruct_name)
        local_sconstruct_path = join(dirname(__file__), sconstruct_name)

        if isfile(sconstruct_path):
            click.secho('Warning: ' + sconstruct_name + ' file already exists',
                        fg='yellow')
            if click.confirm('Do you want to replace it?'):
                self._copy_file(sconstruct_name, sconstruct_path,
                                local_sconstruct_path)
        else:
            self._copy_file(sconstruct_name, sconstruct_path,
                            local_sconstruct_path)

    def _copy_file(self, sconstruct_name,
                   sconstruct_path, local_sconstruct_path):
        click.secho('Creating ' + sconstruct_name + ' file ...')
        with open(sconstruct_path, 'w') as sconstruct:
            with open(local_sconstruct_path, 'r') as local_sconstruct:
                sconstruct.write(local_sconstruct.read())
                click.secho(
                    'File \'' + sconstruct_name +
                    '\' has been successfully created!',
                    fg='green')
