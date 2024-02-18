# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""TODO"""

import click

from apio.managers.project import Project

# ----- Constant for accesing dicctionaries
BOARD = "board"  # -- Key for the board name
FPGA = "fpga"  # -- Key for the fpga
ARCH = "arch"  # -- Key for the FPGA Architecture
TYPE = "type"  # -- Key for the FPGA Type
SIZE = "size"  # -- Key for the FPGA size
PACK = "pack"  # -- Key for the FPGA pack
IDCODE = "idcode"  # -- Key for the FPGA IDCODE


def process_arguments(args, resources):  # noqa
    """TODO"""

    # -- Default configuration
    config = {
        BOARD: None,
        FPGA: None,
        ARCH: None,
        TYPE: None,
        SIZE: None,
        PACK: None,
        IDCODE: None,
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

    debug_config_item(BOARD, proj.board, config)

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

    # -- If board name is given, Check if it is a valid board
    if config[BOARD] and config[BOARD] not in resources.boards:
        raise ValueError(f"unknown board: {config[BOARD]}")

    # -- IF board given, read its configuration
    if config[BOARD] and config[BOARD] in resources.boards:
        fpga = resources.boards.get(config[BOARD]).get(FPGA)
        update_config_item(config, FPGA, fpga)

        # -- Check if the FPGA is correct
        if fpga not in resources.fpgas:
            raise ValueError(f"unknown FPGA: {config[FPGA]}")

        # -- Debug
        update_config_fpga_item(config, ARCH, resources)
        update_config_fpga_item(config, TYPE, resources)
        update_config_fpga_item(config, SIZE, resources)
        update_config_fpga_item(config, PACK, resources)
        update_config_fpga_item(config, IDCODE, resources)

    # -- Debug
    print(f"(Debug) ---> Board: {config[BOARD]}")
    print(f"(Debug) ---> FPGA: {config[FPGA]}")
    print(f"(Debug) ---> FPGA ARCH: {config[ARCH]}")
    print(f"(Debug) ---> FPGA TYPE: {config[TYPE]}")
    print(f"(Debug) ---> FPGA SIZE: {config[SIZE]}")
    print(f"(Debug) ---> FPGA PACK: {config[PACK]}")
    print(f"(Debug) ---> FPGA IDCODE: {config[IDCODE]}")

    # -- Check the current config
    # -- At least it should have arch, type, size and pack
    if not config[FPGA]:
        raise ValueError("Missing FPGA")

    # if not config[ARCH]:
    #    raise ValueError("Missing FPGA architecture")

    if not config[TYPE]:
        raise ValueError("Missing FPGA type")

    if not config[SIZE]:
        raise ValueError("Missing FPGA size")

    if not config[PACK]:
        raise ValueError("Missing FPGA packaging")

    # -- Debug: Store arguments in local variables
    var_verbose = config["verbose"]
    var_topmodule = config["top-module"]

    print(f"DEBUG!!!! TOP-MODULE: {var_topmodule}")

    # click.secho(
    #       "Error: insufficient arguments: missing board",
    #       fg="red",
    #   )
    #   click.secho(
    #       "You have two options:\n"
    #       + "  1) Execute your command with\n"
    #       + "       `--board <boardname>`\n"
    #       + "  2) Create an ini file using\n"
    #       + "       `apio init --board <boardname>`",
    #       fg="yellow",
    #   )
    #   raise ValueError("Missing board")

    # -- Build Scons variables list
    variables = format_vars(
        {
            "fpga_arch": config[ARCH],
            "fpga_size": config[SIZE],
            "fpga_type": config[TYPE],
            "fpga_pack": config[PACK],
            "fpga_idcode": config[IDCODE],
            "verbose_all": var_verbose.get("all"),
            "verbose_yosys": var_verbose.get("yosys"),
            "verbose_pnr": var_verbose.get("pnr"),
            "top_module": var_topmodule,
        }
    )

    return variables, config[BOARD], config[ARCH]


def update_config_fpga_item(config, item, resources):
    """TODO"""

    # -- Read the FPGA pack
    fpga_item = resources.fpgas.get(config[FPGA]).get(item)
    update_config_item(config, item, fpga_item)

    return fpga_item


def update_config_item(config, item, value):
    """TODO"""

    debug_config_item(item, value, config)

    # -- No FPGA pack given by arguments.
    # -- We use the one in the current board
    if config[item] is None:
        config[item] = value
    else:
        # -- Two FPGA pack given. The board FPGA pack and the one
        # -- given by arguments
        # -- It is a contradiction if their names are different
        if value != config[item]:
            raise ValueError(f"contradictory arguments: {value, config[item]}")


def debug_config_item(item: str, proj_item: str, config: dict):
    """Print a Debug message related to the project configuration
    * item: item name to check
    * proj_item: project item value
    * config: Current configuration
    """
    print(f"(Debug): {item}, Project: {proj_item}, Argument: {config[item]}")


def format_vars(args):
    """Format the given vars in the form: 'flag=value'"""
    variables = []
    for key, value in args.items():
        if value:
            variables += [f"{key}={value}"]
    return variables
