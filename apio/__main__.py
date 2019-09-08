# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from os import listdir
from os.path import isfile
from sys import exit as sys_exit

from apio import util

commands_folder = util.get_folder('commands')


class ApioCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in listdir(commands_folder):
            if filename.startswith('__init__'):
                continue
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = util.safe_join(commands_folder, name + '.py')
        if isfile(fn):
            with open(fn) as f:
                code = compile(f.read(), fn, 'exec')
                eval(code, ns, ns)
            return ns.get('cli')


@click.command(cls=ApioCLI, invoke_without_command=True)
@click.pass_context
@click.version_option()
def cli(ctx):

    # Update help structure
    if ctx.invoked_subcommand is None:
        help = ctx.get_help()
        help = help.split('\n')

        setup_help = find_commands_help(help, ['drivers', 'init',
                                               'install', 'uninstall'])
        util_help = find_commands_help(help, ['boards', 'config', 'examples',
                                              'raw', 'system', 'upgrade'])

        help = '\n'.join(help)
        help = help.replace('Commands:\n', 'Project commands:\n')
        help += "\n\nSetup commands:\n"
        help += '\n'.join(setup_help)
        help += "\n\nUtility commands:\n"
        help += '\n'.join(util_help)

        click.secho(help)


def find_commands_help(help, commands):
    commands_help = []
    for line in list(help):
        for command in commands:
            if (' ' + command) in line:
                if line in help:
                    help.remove(line)
                    commands_help.append(line)
    return commands_help


if __name__ == '__main__':  # pragma: no cover
    sys_exit(cli())
