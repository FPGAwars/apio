# Execute functions

import os
import glob
import click
import shutil

from os.path import join, isdir, isfile, dirname, basename

try:
    input = raw_input
except NameError:
    pass


# -- Error messages
EXAMPLE_NOT_FOUND_MSG = """
Sorry, this example does not exist
Use "apio examples -l" for listing all the available examples"""

EXAMPLE_OF_USE_CAD = """
Example of use:
  apio examples -f leds
Copy the leds example files to the current directory"""

EXAMPLE_DIR_FILE = """
To get an example, use the command:
   apio examples -d/-f name"""


class Examples(object):

    def __init__(self):
        self.examples_dir = join(dirname(__file__), '..', 'examples')

    def list_examples(self):
        examples = sorted(os.listdir(self.examples_dir))
        click.echo('')
        for example in examples:
            example_dir = join(self.examples_dir, example)
            info_path = join(example_dir, 'info')
            info = ''
            if isfile(info_path):
                with open(info_path, 'r') as info_file:
                    info = info_file.read().replace('\n', '')
            click.echo(' > ' + example + '  ' + info)
        click.echo(EXAMPLE_DIR_FILE)
        click.echo(EXAMPLE_OF_USE_CAD)
        return

    def copy_example_dir(self, example):
        example_path = join(os.getcwd(), example)
        local_example_path = join(self.examples_dir, example)

        if isdir(local_example_path):
            if isdir(example_path):
                click.echo('Warning: ' + example + ' directory already exists')
                key = input('Do you want to replace it? [Y/N]: ')
                if key == 'y' or key == 'Y':
                    shutil.rmtree(example_path)
                    self._copy_dir(example, local_example_path, example_path)
            elif isfile(example_path):
                click.echo('Warning: ' + example + ' is already a file')
            else:
                self._copy_dir(example, local_example_path, example_path)
        else:
            click.echo(EXAMPLE_NOT_FOUND_MSG)

    def copy_example_files(self, example):
        example_path = os.getcwd()
        local_example_path = join(self.examples_dir, example)

        if isdir(local_example_path):
            self._copy_files(example, local_example_path, example_path)
        else:
            click.echo(EXAMPLE_NOT_FOUND_MSG)

    def _copy_files(self, example, src_path, dest_path):
        click.echo(' Copying ' + example + ' example')
        example_files = glob.glob(join(src_path, '*'))
        for f in example_files:
            filename = basename(f)
            if filename != 'info':
                if isfile(join(dest_path, filename)):
                    click.echo('Warning: ' + filename + ' file already exists')
                    key = input('Do you want to replace it? [Y/N]: ')
                    if key == 'y' or key == 'Y':
                        shutil.copy(f, dest_path)
                elif isdir(join(dest_path, filename)):
                    click.echo('Warning: ' + filename + ' is already a directory')
                else:
                    shutil.copy(f, dest_path)

    def _copy_dir(self, example, src_path, dest_path):
        click.echo(' Creating ' + example + ' directory')
        shutil.copytree(src_path, dest_path)

    def examples_of_use_cad(self):
        return EXAMPLE_OF_USE_CAD
