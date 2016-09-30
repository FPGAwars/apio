# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo, Juan González
# -- Licence GPLv2

import os
import glob
import click
import shutil

from os.path import sep, join, isdir, isfile, dirname, basename

from apio import util

# -- Error messages
EXAMPLE_NOT_FOUND_MSG = """
Warning: this example does not exist
Use `apio examples -l` for listing all the available examples"""

EXAMPLE_OF_USE_CAD = """
Example of use:
   apio examples -f leds
Copy the leds example files to the current directory"""

EXAMPLE_DIR_FILE = """
To get an example, use the command:
   apio examples -d/-f name"""


class Examples(object):

    def __init__(self):
        self.examples_dir = join(util.get_home_dir(), 'packages', 'examples')

    def list_examples(self):
        if isdir(self.examples_dir):
            # examples = sorted(os.listdir(self.examples_dir))
            examples = [dirname(y).replace(self.examples_dir + sep, '')
                        for x in os.walk(self.examples_dir)
                        for y in glob.glob(join(x[0], 'info'))]
            click.secho('')
            for example in examples:
                example_dir = join(self.examples_dir, example)
                if isdir(example_dir):
                    info_path = join(example_dir, 'info')
                    info = ''
                    if isfile(info_path):
                        with open(info_path, 'r') as info_file:
                            info = info_file.read().replace('\n', '')
                    click.secho(' ' + example, fg='blue', bold=True)
                    click.secho('-' * click.get_terminal_size()[0])
                    click.secho(' ' + info)
                    click.secho('')
            click.secho(EXAMPLE_DIR_FILE, fg='green')
            click.secho(EXAMPLE_OF_USE_CAD, fg='green')
        else:
            click.secho('Error: examples are not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install examples', fg='yellow')
            return 1
        return 0

    def copy_example_dir(self, example, project_dir, sayno):
        if isdir(self.examples_dir):

            # -- Target dir not specified
            if project_dir is not None:
                example_path = join(project_dir, example)
            else:
                # -- Not specified: use the current working dir
                example_path = join(util.get_project_dir(), example)

            # -- Get the local example path
            local_example_path = join(self.examples_dir, example)

            if isdir(local_example_path):
                if isdir(example_path):

                    # -- If sayno, do not copy anything
                    if not sayno:
                        click.secho(
                            'Warning: ' + example +
                            ' directory already exists', fg='yellow')

                        if click.confirm('Do you want to replace it?'):
                            shutil.rmtree(example_path)
                            self._copy_dir(example, local_example_path,
                                           example_path)
                elif isfile(example_path):
                    click.secho(
                        'Warning: ' + example + ' is already a file',
                        fg='yellow')
                else:
                    self._copy_dir(example, local_example_path, example_path)
            else:
                click.secho(EXAMPLE_NOT_FOUND_MSG, fg='yellow')
        else:
            click.secho('Error: examples are not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install examples', fg='yellow')
            return 1
        return 0

    def copy_example_files(self, example, project_dir, sayno):
        if isdir(self.examples_dir):

            if project_dir is not None:
                example_path = project_dir
            else:
                example_path = util.get_project_dir()

            local_example_path = join(self.examples_dir, example)

            if isdir(local_example_path):
                self._copy_files(example, local_example_path,
                                 example_path, sayno)
            else:
                click.secho(EXAMPLE_NOT_FOUND_MSG, fg='yellow')
        else:
            click.secho('Error: examples are not installed', fg='red')
            click.secho('Please run:\n'
                        '   apio install examples', fg='yellow')
            return 1
        return 0

    def _copy_files(self, example, src_path, dest_path, sayno):
        click.secho('Copying ' + example + ' example files ...')
        example_files = glob.glob(join(src_path, '*'))
        for f in example_files:
            filename = basename(f)
            if filename != 'info':
                if isfile(join(dest_path, filename)):

                    # -- If sayno, do not copy the file. Move to the next
                    if sayno:
                        continue

                    click.secho(
                        'Warning: ' + filename + ' file already exists',
                        fg='yellow')
                    if click.confirm('Do you want to replace it?'):
                        shutil.copy(f, dest_path)
                elif isdir(join(dest_path, filename)):
                    click.secho(
                        'Warning: ' + filename + ' is already a directory',
                        fg='yellow')
                    return
                else:
                    shutil.copy(f, dest_path)
        click.secho(
            'Example files \'{}\' have been successfully created!'.format(
                example
            ), fg='green')

    def _copy_dir(self, example, src_path, dest_path):
        click.secho('Creating ' + example + ' directory ...')
        shutil.copytree(src_path, dest_path)
        click.secho(
            'Example \'' + example + '\' has been successfully created!',
            fg='green')

    def examples_of_use_cad(self):
        return EXAMPLE_OF_USE_CAD
