# Execute functions

import os
import sys
import util
import click


def run_scons(variables=[]):
    packages_dir = os.path.join(util.get_home_dir(), 'packages')

    # Give the priority to the packages installed by apio
    os.environ['PATH'] = os.pathsep.join(
        [os.path.join(packages_dir, 'toolchain-icestorm', 'bin'), os.environ['PATH']])

    util.exec_command(
        [
            os.path.normpath(sys.executable),  # TODO: find python2 if executed with python3
            os.path.join(packages_dir, 'tool-scons', 'script', 'scons'),
            '-Q'
        ] + variables,
        stdout=util.AsyncPipe(on_run_out),
        stderr=util.AsyncPipe(on_run_err)
    )


def on_run_out(line):
    click.secho(line)


def on_run_err(line):
    click.secho(line)
