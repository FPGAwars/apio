# Execute functions

import os
import click

from os.path import join, dirname, isfile

try:
    input = raw_input
except NameError:
    pass


class Example(object):

    def create_example(self):
        example_path = join(os.getcwd())
        local_example_path = join(dirname(__file__), '..', 'examples', 'leds')

        self._create_file('leds.v', example_path, local_example_path)
        self._create_file('leds.pcf', example_path, local_example_path)

    def _create_file(self, filename, path, local_path):
        if isfile(join(path, filename)):
            click.echo('Warning: ' + filename + ' file already exists')
            key = input('Do you want to replace it? [Y/N]: ')
            if key == 'y' or key == 'Y':
                self._copy_file(filename, path, local_path)
        else:
            self._copy_file(filename, path, local_path)

    def _copy_file(self, filename, path, local_path):
        click.echo(' Creating ' + filename + ' file...')
        with open(join(path, filename), 'w') as _file:
            with open(join(local_path, filename), 'r') as _local_file:
                _file.write(_local_file.read())
                click.echo(' Done')
