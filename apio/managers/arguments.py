# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""TODO"""

from os.path import isfile

import click

from apio.managers.project import Project

# ----- Constant for accesing dicctionaries
# -- Key for the board name
BOARD = "board"


# Too many local variables (23/15)
# pylint: disable=R0914
# Too many nested blocks (6/5)
# pylint: disable=R1702
# Too many branches (57/12)
# pylint: disable=R0912
# Too many statements (147/50)
# pylint: disable=R0915
def process_arguments(args, resources):  # noqa
    """TODO"""

    # -- Default configuration
    config = {
        BOARD: None,
        "arch": None,
        "fpga": None,
        "size": None,
        "type": None,
        "pack": None,
        "idcode": None,
        "verbose": None,
        "top-module": None,
    }

    # -- Add arguments to default config
    config.update(args)

    # -- Read the apio project file (apio.ini)
    proj = Project()
    proj.read()

    # -- proj.board:
    # --   * None: No apio.ini file
    # --   * "name": Board name (str)

    print(f"Debug. Project board: {proj.board}")
    print(f"Debug. Argument board: {config[BOARD]}")

    # -- Board name given in the command line
    if config[BOARD]:

        # -- If there is a project file (apio.ini) the board
        # -- give by command line overrides it
        # -- (command line has the highest priority)
        if proj.board:
            click.secho("Info: ignore apio.ini board", fg="yellow")

    # -- Board name given in the project file
    else:
        # -- ...read it from the apio.ini file
        config[BOARD] = proj.board

    # -- Debug
    print(f"(Debug) ---> Board: {config[BOARD]}")

    # -- If board name is given, Check if it is a valid board
    if config[BOARD] and config[BOARD] not in resources.boards:
        raise ValueError(f"unknown board: {config[BOARD]}")

    print(f"Debug. FPGA: {config['fpga']}")

    # -- Debug: Store arguments in local variables
    var_board = config[BOARD]
    var_fpga = config["fpga"]
    var_size = config["size"]
    var_arch = config["arch"]
    var_type = config["type"]
    var_pack = config["pack"]
    var_idcode = config["idcode"]
    var_verbose = config["verbose"]
    var_topmodule = config["top-module"]

    print(f"DEBUG!!!! TOP-MODULE: {var_topmodule}")

    if config[BOARD]:
        if var_board in resources.boards:
            fpga = resources.boards.get(var_board).get("fpga")
            if fpga in resources.fpgas:
                fpga_arch = resources.fpgas.get(fpga).get("arch")
                fpga_size = resources.fpgas.get(fpga).get("size")
                fpga_type = resources.fpgas.get(fpga).get("type")
                fpga_pack = resources.fpgas.get(fpga).get("pack")
                fpga_idcode = resources.fpgas.get(fpga).get("idcode")

                redundant_arguments = []
                contradictory_arguments = []

                if var_fpga:
                    if var_fpga in resources.fpgas:
                        if var_fpga == fpga:
                            # Redundant argument
                            redundant_arguments += ["fpga"]
                        else:
                            # Contradictory argument
                            contradictory_arguments += ["fpga"]
                    else:
                        # Unknown FPGA
                        raise ValueError(f"unknown FPGA: {var_fpga}")

                if var_size:
                    if var_size == fpga_size:
                        # Redundant argument
                        redundant_arguments += ["size"]
                    else:
                        # Contradictory argument
                        contradictory_arguments += ["size"]

                if var_type:
                    if var_type == fpga_type:
                        # Redundant argument
                        redundant_arguments += ["type"]
                    else:
                        # Contradictory argument
                        contradictory_arguments += ["type"]

                if var_pack:
                    if var_pack == fpga_pack:
                        # Redundant argument
                        redundant_arguments += ["pack"]
                    else:
                        # Contradictory argument
                        contradictory_arguments += ["pack"]

                if var_idcode:
                    if var_idcode == fpga_idcode:
                        # Redundant argument
                        redundant_arguments += ["idcode"]
                    else:
                        # Contradictory argument
                        contradictory_arguments += ["idcode"]

                if redundant_arguments:
                    # Redundant argument
                    warning_str = ", ".join(redundant_arguments)
                    click.secho(
                        f"Warning: redundant arguments: {warning_str}",
                        fg="yellow",
                    )

                if contradictory_arguments:
                    # Contradictory argument
                    error_str = ", ".join(contradictory_arguments)
                    raise ValueError(f"contradictory arguments: {error_str}")
            else:
                # Unknown FPGA
                pass
        else:
            # Unknown board
            raise ValueError(f"unknown board: {var_board}")
    else:
        print("Debug: NO BOARD!!")
        if var_fpga:
            if isfile("apio.ini"):
                click.secho("Info: ignore apio.ini board", fg="yellow")
            if var_fpga in resources.fpgas:
                fpga_arch = resources.fpgas.get(var_fpga).get("arch")
                fpga_size = resources.fpgas.get(var_fpga).get("size")
                fpga_type = resources.fpgas.get(var_fpga).get("type")
                fpga_pack = resources.fpgas.get(var_fpga).get("pack")
                fpga_idcode = resources.fpgas.get(var_fpga).get("idcode")

                redundant_arguments = []
                contradictory_arguments = []

                if var_size:
                    if var_size == fpga_size:
                        # Redundant argument
                        redundant_arguments += ["size"]
                    else:
                        # Contradictory argument
                        contradictory_arguments += ["size"]

                if var_type:
                    if var_type == fpga_type:
                        # Redundant argument
                        redundant_arguments += ["type"]
                    else:
                        # Contradictory argument
                        contradictory_arguments += ["type"]

                if var_pack:
                    if var_pack == fpga_pack:
                        # Redundant argument
                        redundant_arguments += ["pack"]
                    else:
                        # Contradictory argument
                        contradictory_arguments += ["pack"]

                if var_idcode:
                    if var_idcode == fpga_idcode:
                        # Redundant argument
                        redundant_arguments += ["idcode"]
                    else:
                        # Contradictory argument
                        contradictory_arguments += ["idcode"]

                if redundant_arguments:
                    # Redundant argument
                    warning_str = ", ".join(redundant_arguments)
                    click.secho(
                        f"Warning: redundant arguments: {warning_str}",
                        fg="yellow",
                    )

                if contradictory_arguments:
                    # Contradictory argument
                    error_str = ", ".join(contradictory_arguments)
                    raise ValueError(f"contradictory arguments: {error_str}")
            else:
                # Unknown FPGA
                raise ValueError(f"unknown FPGA: {var_fpga}")
        else:
            if var_size and var_type and var_pack and var_arch:
                if isfile("apio.ini"):
                    click.secho("Info: ignore apio.ini board", fg="yellow")
                fpga_arch = var_arch
                fpga_size = var_size
                fpga_type = var_type
                fpga_pack = var_pack
                fpga_idcode = var_idcode
            else:
                print("LLEGA AQUI!!!!")
                if not var_size and not var_type and not var_pack:
                    # No arguments: use apio.ini board
                    proj = Project()
                    proj.read()
                    if proj.board:
                        var_board = proj.board
                        if var_board in resources.boards:
                            fpga = resources.boards.get(var_board).get("fpga")
                            fpga_arch = resources.fpgas.get(fpga).get("arch")
                            fpga_size = resources.fpgas.get(fpga).get("size")
                            fpga_type = resources.fpgas.get(fpga).get("type")
                            fpga_pack = resources.fpgas.get(fpga).get("pack")
                            fpga_idcode = resources.fpgas.get(fpga).get(
                                "idcode"
                            )
                        else:
                            # Unknown board
                            raise ValueError(f"unknown board: {var_board}")
                    else:
                        click.secho(
                            "Error: insufficient arguments: missing board",
                            fg="red",
                        )
                        click.secho(
                            "You have two options:\n"
                            + "  1) Execute your command with\n"
                            + "       `--board <boardname>`\n"
                            + "  2) Create an ini file using\n"
                            + "       `apio init --board <boardname>`",
                            fg="yellow",
                        )
                        raise ValueError("Missing board")
                else:
                    if isfile("apio.ini"):
                        click.secho("Info: ignore apio.ini board", fg="yellow")
                    # Insufficient arguments
                    missing = []
                    if not var_size:
                        missing += ["size"]
                    if not var_type:
                        missing += ["type"]
                    if not var_pack:
                        missing += ["pack"]
                    raise ValueError(
                        f"insufficient arguments: missing {', '.join(missing)}"
                    )

    # -- Build Scons variables list
    variables = format_vars(
        {
            "fpga_arch": fpga_arch,
            "fpga_size": fpga_size,
            "fpga_type": fpga_type,
            "fpga_pack": fpga_pack,
            "fpga_idcode": fpga_idcode,
            "verbose_all": var_verbose.get("all"),
            "verbose_yosys": var_verbose.get("yosys"),
            "verbose_pnr": var_verbose.get("pnr"),
            "top_module": var_topmodule,
        }
    )

    return variables, var_board, fpga_arch


def format_vars(args):
    """Format the given vars in the form: 'flag=value'"""
    variables = []
    for key, value in args.items():
        if value:
            variables += [f"{key}={value}"]
    return variables
