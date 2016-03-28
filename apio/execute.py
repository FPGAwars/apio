# Execute functions

import os
import sys
import click
import platform

from os.path import join, dirname, isdir, isfile, expanduser

from . import util


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
            print('System tools are not installed. Please run:\n'
                  '  apio install --system')

    def _on_run_out(self, line):
        click.secho(line)


class SCons(object):

    def __init__(self):
        self.err_enable = True
        self.scons_variables = []

    def run(self, variables=[]):
        self.scons_variables = variables

        packages_dir = os.path.join(util.get_home_dir(), 'packages')

        # Give the priority to the packages installed by apio
        os.environ['PATH'] = os.pathsep.join(
            [os.path.join(packages_dir, 'toolchain-icestorm', 'bin'), os.environ['PATH']])

        util.exec_command(
            [
                os.path.normpath(sys.executable),
                os.path.join(packages_dir, 'tool-scons', 'script', 'scons'),
                '-Q'
            ] + variables,
            stdout=util.AsyncPipe(self._on_run_out),
            stderr=util.AsyncPipe(self._on_run_err)
        )

    def _on_run_out(self, line):
        click.secho(line)

    def _on_run_err(self, line):
        if 'No SConstruct file found' in line:
            self.err_enable = False
            click.secho('Using default SConstruct file\n')
            self.run(self.scons_variables + ['-f', join(dirname(__file__), 'SConstruct')])

        if self.err_enable:
            click.secho(line)

    def create_sconstruct(self):
        sconstruct_name = 'SConstruct'
        sconstruct_path = join(os.getcwd(), sconstruct_name)
        local_sconstruct_path = join(dirname(__file__), sconstruct_name)

        if not isfile(sconstruct_path):
            click.echo('Creating SConstruct file...')
            with open(sconstruct_path, 'w') as sconstruct:
                with open(local_sconstruct_path, 'r') as local_sconstruct:
                    sconstruct.write(local_sconstruct.read())
                    click.echo('Done')
        else:
            click.echo('Warning: SConstruct file already exists')
