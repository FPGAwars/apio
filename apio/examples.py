# Execute functions

import os
import click
import shutil

from os.path import join, dirname, isdir

try:
    input = raw_input
except NameError:
    pass


class Examples(object):

    def __init__(self):
        self.examples_dir = join(dirname(__file__), '..', 'examples')

    def list_examples(self):
        return sorted(os.listdir(self.examples_dir))

    def copy_example(self, example):
        example_path = join(os.getcwd(), example)
        local_example_path = join(self.examples_dir, example)

        if isdir(local_example_path):
            if isdir(example_path):
                click.echo('Warning: ' + example + ' directory already exists')
                key = input('Do you want to replace it? [Y/N]: ')
                if key == 'y' or key == 'Y':
                    shutil.rmtree(example_path)
                    self._copy_dir(example, local_example_path, example_path)
            else:
                self._copy_dir(example, local_example_path, example_path)
        else:
            click.echo('Sorry, this example does not exist.')

    def _copy_dir(self, example, local_example_path, example_path):
        click.echo(' Creating ' + example + ' example')
        shutil.copytree(local_example_path, example_path)
