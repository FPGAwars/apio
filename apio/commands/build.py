"""DOC: TODO"""
# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2

import click

from apio.managers.scons import SCons


# R0913: Too many arguments (6/5)
# pylint: disable=R0913
# pylint: disable=W0622
# pylint: disable=R0801
@click.command("build")
@click.pass_context
@click.option(
    "-b", "--board", type=str, metavar="board", help="Set the board."
)
@click.option("--fpga", type=str, metavar="fpga", help="Set the FPGA.")
@click.option(
    "--size", type=str, metavar="size", help="Set the FPGA type (1k/8k)."
)
@click.option(
    "--type", type=str, metavar="type", help="Set the FPGA type (hx/lp)."
)
@click.option(
    "--pack", type=str, metavar="package", help="Set the FPGA package."
)
@click.option(
    "-p",
    "--project-dir",
    type=str,
    metavar="path",
    help="Set the target directory for the project.",
)
@click.option(
    "-v",
    "--verbose",
    is_flag=True,
    help="Show the entire output of the command.",
)
@click.option(
    "--verbose-yosys",
    is_flag=True,
    help="Show the yosys output of the command.",
)
@click.option(
    "--verbose-pnr", is_flag=True, help="Show the pnr output of the command."
)
@click.option(
    "--top-module",
    type=str,
    metavar="top_module",
    help="Set the top level module (w/o .v ending) for build.",
)
def cli(
    ctx,
    board,
    fpga,
    pack,
    type,
    size,
    project_dir,
    verbose,
    verbose_yosys,
    verbose_pnr,
    top_module,
):
    """Synthesize the bitstream."""

    # The bitstream is generated from the source files (verilog)
    # by means of the scons tool
    # https://www.scons.org/documentation.html

    # -- Crete the scons object
    scons = SCons(project_dir)

    # -- Build the project with the given parameters
    exit_code = scons.build(
        {
            "board": board,
            "fpga": fpga,
            "size": size,
            "type": type,
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
