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
BOARD = "board"  # -- Key for the board name
FPGA = "fpga"  # -- Key for the fpga
ARCH = "arch"  # -- Key for the FPGA Architecture
TYPE = "type"  # -- Key for the FPGA Type
SIZE = "size"  # -- Key for the FPGA size
PACK = "pack"  # -- Key for the FPGA pack
IDCODE = "idcode"  # -- Key for the FPGA IDCODE


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

    print(f"Debug. Project board: {proj.board}")
    print(f"Debug. Argument board: {config[BOARD]}")

    # -- Debug
    fpga = ""
    fpga_arch = ""
    fpga_type = ""
    fpga_size = ""
    fpga_pack = ""
    fpga_idcode = ""

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

    # -- IF board given, read its configuration
    if config[BOARD] and config[BOARD] in resources.boards:
        fpga = resources.boards.get(config[BOARD]).get(FPGA)
        print(f"Debug. Argument FPGA: {config[FPGA]}")
        print(f"Debug. Project FPGA: {fpga}")

        # -- No FPGA given by arguments.
        # -- We use the one in the current board
        if config[FPGA] is None:
            config[FPGA] = fpga
        else:
            # -- Two FPGAs given. The board FPGA and the one
            # -- given by arguments
            # -- It is a contradiction if their names are different
            if fpga != config[FPGA]:
                raise ValueError(
                    f"contradictory arguments: {fpga, config[FPGA]}"
                )

        # -- Check if the FPGA is correct
        if fpga not in resources.fpgas:
            raise ValueError(f"unknown FPGA: {config[FPGA]}")

        # -- Debug
        print(f"(Debug) ---> FPGA: {config[FPGA]}")

        # -- Read the FPGA configuration (architecture)
        fpga_arch = resources.fpgas.get(fpga).get(ARCH)

        print(f"Debug. Argument Arch: {config[ARCH]}")
        print(f"Debug. Project Arch: {fpga_arch}")

        # -- No FPGA Arch given by arguments.
        # -- We use the one in the current board
        if config[ARCH] is None:
            config[ARCH] = fpga_arch
        else:
            # -- Two FPGA Architectures given. The board FPGA Arch and the one
            # -- given by arguments
            # -- It is a contradiction if their names are different
            if fpga_arch != config[ARCH]:
                raise ValueError(
                    f"contradictory arguments: {fpga_arch, config[FPGA]}"
                )

        # -- Debug
        print(f"(Debug) ---> FPGA ARCH: {config[ARCH]}")

        # -- Read the FPGA type
        fpga_type = resources.fpgas.get(fpga).get(TYPE)

        print(f"Debug. Argument Type: {config[TYPE]}")
        print(f"Debug. Project Type: {fpga_type}")

        # -- No FPGA type given by arguments.
        # -- We use the one in the current board
        if config[TYPE] is None:
            config[TYPE] = fpga_type
        else:
            # -- Two FPGA Types given. The board FPGA Type and the one
            # -- given by arguments
            # -- It is a contradiction if their names are different
            if fpga_type != config[TYPE]:
                raise ValueError(
                    f"contradictory arguments: {fpga_type, config[TYPE]}"
                )

        # -- Debug
        print(f"(Debug) ---> FPGA TYPE: {config[TYPE]}")

        # -- Read the FPGA size
        fpga_size = resources.fpgas.get(fpga).get(SIZE)

        print(f"Debug. Argument Size: {config[SIZE]}")
        print(f"Debug. Project Size: {fpga_size}")

        # -- No FPGA size given by arguments.
        # -- We use the one in the current board
        if config[SIZE] is None:
            config[SIZE] = fpga_size
        else:
            # -- Two FPGA size given. The board FPGA Size and the one
            # -- given by arguments
            # -- It is a contradiction if their names are different
            if fpga_size != config[SIZE]:
                raise ValueError(
                    f"contradictory arguments: {fpga_size, config[SIZE]}"
                )

        # -- Debug
        print(f"(Debug) ---> FPGA SIZE: {config[SIZE]}")

        # -- Read the FPGA pack
        fpga_pack = resources.fpgas.get(fpga).get(PACK)

        print(f"Debug. Argument Pack: {config[PACK]}")
        print(f"Debug. Project Pack: {fpga_pack}")

        # -- No FPGA pack given by arguments.
        # -- We use the one in the current board
        if config[PACK] is None:
            config[PACK] = fpga_pack
        else:
            # -- Two FPGA pack given. The board FPGA pack and the one
            # -- given by arguments
            # -- It is a contradiction if their names are different
            if fpga_pack != config[PACK]:
                raise ValueError(
                    f"contradictory arguments: {fpga_pack, config[PACK]}"
                )

        # -- Debug
        print(f"(Debug) ---> FPGA PACK: {config[PACK]}")

        # -- Read the FPGA idcode
        fpga_idcode = resources.fpgas.get(fpga).get(IDCODE)
        fpga_idcode = resources.fpgas.get(fpga).get("idcode")

        print(f"Debug. Argument Idcode: {config[IDCODE]}")
        print(f"Debug. Project Idcode: {fpga_idcode}")

        # -- No FPGA idcode given by arguments.
        # -- We use the one in the current board
        if config[IDCODE] is None:
            config[IDCODE] = fpga_idcode
        else:
            # -- Two FPGA idcode given. The board FPGA idcode and the one
            # -- given by arguments
            # -- It is a contradiction if their names are different
            if fpga_idcode != config[IDCODE]:
                raise ValueError(
                    f"contradictory arguments: {fpga_idcode, config[IDCODE]}"
                )

        # -- Debug
        print(f"(Debug) ---> FPGA IDCODE: {config[IDCODE]}")

    # -- Debug: Store arguments in local variables
    var_board = config[BOARD]
    var_fpga = config[FPGA]
    var_arch = config[ARCH]
    var_type = config[TYPE]
    var_size = config[SIZE]
    var_pack = config[PACK]
    var_idcode = config[IDCODE]
    var_verbose = config["verbose"]
    var_topmodule = config["top-module"]

    print(f"DEBUG!!!! TOP-MODULE: {var_topmodule}")

    if config[BOARD]:

        redundant_arguments = []
        contradictory_arguments = []

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
