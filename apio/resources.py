# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import os
import json
import click

from apio.profile import Profile

BOARDS_MSG = """
Use `apio init --board <boardname>` for creating a new apio """ \
"""project for that board"""


class Resources(object):

    def __init__(self):
        self.packages = self._load_resource('packages')
        self.boards = self._load_resource('boards')
        self.fpgas = self._load_resource('fpgas')

    def _load_resource(self, name):
        resource = None
        filepath = os.path.join(
            os.path.dirname(__file__), 'resources', name + '.json')
        with open(filepath, 'r') as f:
            # Load the JSON file
            resource = json.loads(f.read())
        return resource

    def list_packages(self, installed=True, notinstalled=True):
        """Return a list with all the installed/notinstalled packages"""

        self.profile = Profile()

        # Classify packages
        installed_packages = []
        notinstalled_packages = []

        for package in self.packages:
            data = {
                'name': package,
                'version': None,
                'description': self.packages[package]['description']
            }
            if self.profile.check_package(package):
                data['version'] = self.profile.get_version(package)
                installed_packages += [data]
            else:
                notinstalled_packages += [data]

        # Print tables
        terminal_width, _ = click.get_terminal_size()

        if installed and installed_packages:

            # - Print installed packages table
            click.echo('\nInstalled packages:\n')

            PACKAGELIST_TPL = ('{name:20} {description:30} {version:<8}')

            click.echo('-' * terminal_width)
            click.echo(PACKAGELIST_TPL.format(
                name=click.style('Name', fg='cyan'), version='Version',
                description='Description'))
            click.echo('-' * terminal_width)

            for package in installed_packages:
                click.echo(PACKAGELIST_TPL.format(
                    name=click.style(package['name'], fg='cyan'),
                    version=package['version'],
                    description=package['description']))

        if notinstalled and notinstalled_packages:

            # - Print not installed packages table
            click.echo('\nNot installed packages:\n')

            PACKAGELIST_TPL = ('{name:20} {description:30}')

            click.echo('-' * terminal_width)
            click.echo(PACKAGELIST_TPL.format(
                name=click.style('Name', fg='yellow'),
                description='Description'))
            click.echo('-' * terminal_width)

            for package in notinstalled_packages:
                click.echo(PACKAGELIST_TPL.format(
                    name=click.style(package['name'], fg='yellow'),
                    description=package['description']))

    def list_boards(self):
        """Return a list with all the supported boards"""

        # Print table
        click.echo('\nSupported boards:\n')

        BOARDLIST_TPL = ('{board:22} {fpga:20} {type:<5} {size:<5} {pack:<10}')
        terminal_width, _ = click.get_terminal_size()

        click.echo('-' * terminal_width)
        click.echo(BOARDLIST_TPL.format(
            board=click.style('Board', fg='cyan'), fpga='FPGA', type='Type',
            size='Size', pack='Pack'))
        click.echo('-' * terminal_width)

        for board in self.boards:
            fpga = self.boards[board]['fpga']
            click.echo(BOARDLIST_TPL.format(
                board=click.style(board, fg='cyan'),
                fpga=fpga,
                type=self.fpgas[fpga]['type'],
                size=self.fpgas[fpga]['size'],
                pack=self.fpgas[fpga]['pack']))

        click.secho(BOARDS_MSG, fg='green')

    def list_fpgas(self):
        """Return a list with all the supported FPGAs"""

        # Print table
        click.echo('\nSupported FPGAs:\n')

        FPGALIST_TPL = ('{fpga:30} {type:<5} {size:<5} {pack:<10}')
        terminal_width, _ = click.get_terminal_size()

        click.echo('-' * terminal_width)
        click.echo(FPGALIST_TPL.format(
            fpga=click.style('FPGA', fg='cyan'), type='Type',
            size='Size', pack='Pack'))
        click.echo('-' * terminal_width)

        for fpga in self.fpgas:
            click.echo(FPGALIST_TPL.format(
                fpga=click.style(fpga, fg='cyan'),
                type=self.fpgas[fpga]['type'],
                size=self.fpgas[fpga]['size'],
                pack=self.fpgas[fpga]['pack']))
