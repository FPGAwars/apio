# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- Licence GPLv2
"""Main implementation of APIO BUILD command"""


import click
from apio.managers.scons import SCons
from apio import util
from apio.commands import options


@click.command("build", context_settings=util.context_settings())
@click.pass_context
@options.board
@options.fpga
@options.size
@options.type_
@options.pack
@options.project_dir
@options.verbose
@options.verbose_yosys
@options.verbose_pnr
@options.top_module
def cli(ctx, **kwargs):
    """Synthesize the bitstream."""
    # -- Extract the arguments
    project_dir = kwargs[options.PROJECT_DIR]
    board = kwargs[options.BOARD]
    fpga = kwargs[options.FPGA]
    pack = kwargs[options.PACK]
    _type = kwargs[options.TYPE]
    size = kwargs[options.SIZE]
    verbose = kwargs[options.VERBOSE]
    verbose_yosys = kwargs[options.VERBOSE_YOSYS]
    verbose_pnr = kwargs[options.VERBOSE_PNR]
    top_module = kwargs[options.TOP_MODULE]

    # The bitstream is generated from the source files (verilog)
    # by means of the scons tool
    # https://www.scons.org/documentation.html

    # -- Create the scons object
    scons = SCons(project_dir)

    # R0801: Similar lines in 2 files
    # pylint: disable=R0801
    # -- Build the project with the given parameters
    exit_code = scons.build(
        {
            "board": board,
            "fpga": fpga,
            "size": size,
            "type": _type,
            "pack": pack,
            "verbose": {
                "all": verbose,
                "yosys": verbose_yosys,
                "pnr": verbose_pnr,
            },
            "top-module": top_module,
        }
    )

    # -- Done!
    ctx.exit(exit_code)


# Advanced notes: https://github.com/FPGAwars/apio/wiki/Commands#apio-build
