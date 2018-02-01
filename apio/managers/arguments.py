# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from os.path import isfile

from apio.managers.project import Project


def process_arguments(args, resources):  # noqa
    # -- Check arguments
    var_board = args.get('board')
    var_fpga = args.get('fpga')
    var_size = args.get('size')
    var_type = args.get('type')
    var_pack = args.get('pack')
    var_verbose = args.get('verbose')

    if var_board:
        if isfile('apio.ini'):
            click.secho('Info: ignore apio.ini board', fg='yellow')
        if var_board in resources.boards:
            fpga = resources.boards.get(var_board).get('fpga')
            if fpga in resources.fpgas:
                fpga_size = resources.fpgas.get(fpga).get('size')
                fpga_type = resources.fpgas.get(fpga).get('type')
                fpga_pack = resources.fpgas.get(fpga).get('pack')

                redundant_arguments = []
                contradictory_arguments = []

                if var_fpga:
                    if var_fpga in resources.fpgas:
                        if var_fpga == fpga:
                            # Redundant argument
                            redundant_arguments += ['fpga']
                        else:
                            # Contradictory argument
                            contradictory_arguments += ['fpga']
                    else:
                        # Unknown FPGA
                        raise Exception('unknown FPGA: {0}'.format(var_fpga))

                if var_size:
                    if var_size == fpga_size:
                        # Redundant argument
                        redundant_arguments += ['size']
                    else:
                        # Contradictory argument
                        contradictory_arguments += ['size']

                if var_type:
                    if var_type == fpga_type:
                        # Redundant argument
                        redundant_arguments += ['type']
                    else:
                        # Contradictory argument
                        contradictory_arguments += ['type']

                if var_pack:
                    if var_pack == fpga_pack:
                        # Redundant argument
                        redundant_arguments += ['pack']
                    else:
                        # Contradictory argument
                        contradictory_arguments += ['pack']

                if redundant_arguments:
                    # Redundant argument
                    click.secho(
                        'Warning: redundant arguments: {}'.format(
                            ', '.join(redundant_arguments)), fg='yellow')

                if contradictory_arguments:
                    # Contradictory argument
                    raise Exception('contradictory arguments: {}'.format(
                                        ', '.join(contradictory_arguments)))
            else:
                # Unknown FPGA
                pass
        else:
            # Unknown board
            raise Exception('unknown board: {0}'.format(var_board))
    else:
        if var_fpga:
            if isfile('apio.ini'):
                click.secho('Info: ignore apio.ini board', fg='yellow')
            if var_fpga in resources.fpgas:
                fpga_size = resources.fpgas.get(var_fpga).get('size')
                fpga_type = resources.fpgas.get(var_fpga).get('type')
                fpga_pack = resources.fpgas.get(var_fpga).get('pack')

                redundant_arguments = []
                contradictory_arguments = []

                if var_size:
                    if var_size == fpga_size:
                        # Redundant argument
                        redundant_arguments += ['size']
                    else:
                        # Contradictory argument
                        contradictory_arguments += ['size']

                if var_type:
                    if var_type == fpga_type:
                        # Redundant argument
                        redundant_arguments += ['type']
                    else:
                        # Contradictory argument
                        contradictory_arguments += ['type']

                if var_pack:
                    if var_pack == fpga_pack:
                        # Redundant argument
                        redundant_arguments += ['pack']
                    else:
                        # Contradictory argument
                        contradictory_arguments += ['pack']

                if redundant_arguments:
                    # Redundant argument
                    click.secho(
                        'Warning: redundant arguments: {}'.format(
                            ', '.join(redundant_arguments)), fg='yellow')

                if contradictory_arguments:
                    # Contradictory argument
                    raise Exception('contradictory arguments: {}'.format(
                                        ', '.join(contradictory_arguments)))
            else:
                # Unknown FPGA
                raise Exception('unknown FPGA: {0}'.format(var_fpga))
        else:
            if var_size and var_type and var_pack:
                if isfile('apio.ini'):
                    click.secho('Info: ignore apio.ini board', fg='yellow')
                fpga_size = var_size
                fpga_type = var_type
                fpga_pack = var_pack
            else:
                if not var_size and not var_type and not var_pack:
                    # No arguments: use apio.ini board
                    p = Project()
                    p.read()
                    if p.board:
                        var_board = p.board
                        click.secho(
                            'Board: {}'.format(
                                var_board))
                        fpga = resources.boards.get(var_board).get('fpga')
                        fpga_size = resources.fpgas.get(fpga).get('size')
                        fpga_type = resources.fpgas.get(fpga).get('type')
                        fpga_pack = resources.fpgas.get(fpga).get('pack')
                    else:
                        click.secho(
                            'Error: insufficient arguments: missing board',
                            fg='red')
                        click.secho(
                            'You have two options:\n' +
                            '  1) Execute your command with\n' +
                            '       `--board <boardname>`\n' +
                            '  2) Create an ini file using\n' +
                            '       `apio init --board <boardname>`',
                            fg='yellow')
                        raise Exception
                else:
                    if isfile('apio.ini'):
                        click.secho('Info: ignore apio.ini board',
                                    fg='yellow')
                    # Insufficient arguments
                    missing = []
                    if not var_size:
                        missing += ['size']
                    if not var_type:
                        missing += ['type']
                    if not var_pack:
                        missing += ['pack']
                    raise Exception(
                        'insufficient arguments: missing {}'.format(
                            ', '.join(missing)))

    # -- Build Scons variables list
    variables = format_vars({
        'fpga_size': fpga_size,
        'fpga_type': fpga_type,
        'fpga_pack': fpga_pack,
        'verbose_all': var_verbose.get('all'),
        'verbose_yosys': var_verbose.get('yosys'),
        'verbose_arachne': var_verbose.get('arachne')
    })

    return variables, var_board


def format_vars(args):
    """Format the given vars in the form: 'flag=value'"""
    variables = []
    for key, value in args.items():
        if value:
            variables += ['{0}={1}'.format(key, value)]
    return variables
