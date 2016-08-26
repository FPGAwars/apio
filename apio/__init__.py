# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from os import listdir
from os.path import isfile, join, dirname
from sys import exit as sys_exit


commands_folder = join(dirname(__file__), 'commands')


class ApioCLI(click.MultiCommand):

    def list_commands(self, ctx):
        rv = []
        for filename in listdir(commands_folder):
            if filename.startswith("__init__"):
                continue
            if filename.endswith('.py'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        ns = {}
        fn = join(commands_folder, name + '.py')
        if isfile(fn):
            with open(fn) as f:
                code = compile(f.read(), fn, 'exec')
                eval(code, ns, ns)
            return ns['cli']


@click.command(cls=ApioCLI, invoke_without_command=True)
@click.pass_context
@click.version_option()
def cli(ctx):
    """
    Experimental micro-ecosystem for open FPGAs
    """

    # Update help structure
    if ctx.invoked_subcommand is None:
        env_help = []
        env_commands = ['boards', 'drivers', 'examples', 'init',
                        'install', 'system', 'uninstall', 'upgrade']

        help = ctx.get_help()
        help = help.split('\n')

        # Find env commands' lines
        for line in list(help):
            for command in env_commands:
                if (' ' + command) in line:
                    if line in help:
                        help.remove(line)
                        env_help.append(line)

        help = '\n'.join(help)
        help = help.replace('Commands:\n', 'Code commands:\n')
        help += "\n\nEnvironment commands:\n"
        help += '\n'.join(env_help)

        click.secho(help)


if __name__ == '__main__':  # pragma: no cover
    sys_exit(cli())
