# Execute functions

import os
import sys
import util
import click

from os.path import join, dirname, isfile


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
            stdout=util.AsyncPipe(self.on_run_out),
            stderr=util.AsyncPipe(self.on_run_err)
        )

    def on_run_out(self, line):
        click.secho(line)

    def on_run_err(self, line):
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
