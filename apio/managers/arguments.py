# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Utilities for procesing the arguments passed to apio commands"""

from functools import wraps

import click
from apio.managers.project import Project

# -- Class for accesing api resources (boards, fpgas...)
from apio.resources import Resources


# ----- Constant for accesing dicctionaries
BOARD = "board"  # -- Key for the board name
FPGA = "fpga"  # -- Key for the fpga
ARCH = "arch"  # -- Key for the FPGA Architecture
TYPE = "type"  # -- Key for the FPGA Type
SIZE = "size"  # -- Key for the FPGA size
PACK = "pack"  # -- Key for the FPGA pack
IDCODE = "idcode"  # -- Key for the FPGA IDCODE
VERBOSE = "verbose"  # -- Key for the Verbose flag
ALL = "all"  # -- Key for Verbose all
YOSYS = "yosys"  # -- Key for Verbose-yosys
PNR = "pnr"  # -- Key for Verbose-pnr
TOP_MODULE = "top-module"  # -- Key for top-module
TESTBENCH = "testbench"  # -- Key for testbench file name


def debug_params(fun):
    """DEBUG. Use it as a decorator. It prints the received arguments
    and the return value
    INPUTS:
      * fun: Function to DEBUG
    """

    @wraps(fun)
    def outer(*args):

        # -- Print the arguments
        print(f"--> DEBUG!. Function {fun.__name__}(). BEGIN")
        print("    * Arguments:")
        for arg in args:

            # -- Print all the key,values if it is a dictionary
            if isinstance(arg, dict):
                print("        * Dict:")
                for key, value in arg.items():
                    print(f"          * {key}: {value}")

            # -- Print the plain argument if it is not a dicctionary
            else:
                print(f"        * {arg}")
        print()

        # -- Call the function
        result = fun(*args)

        # -- Print its output
        print(f"--> DEBUG!. Function {fun.__name__}(). END")
        print("     Returns: ")

        # -- The return object always is a tuple
        if isinstance(result, tuple):

            # -- Print all the values in the tuple
            for value in result:
                print(f"      * {value}")

        # -- But just in case it is not a tuple (because of an error...)
        else:
            print(f"      * No tuple: {result}")
        print()

        return result

    return outer


# R0912: Too many branches (14/12)
# pylint: disable=R0912
# @debug_params
def process_arguments(
    config_ini: dict, resources: type[Resources]
) -> tuple:  # noqa
    """Get the final CONFIGURATION, depending on the board and
    arguments passed in the command line.
    The config_ini parameter has higher priority. If not specified,
    they are read from the Project file (apio.ini)
    * INPUTS:
       * config_ini: Dictionary with the initial configuration:
         {
           'board': str,  //-- Board name
           'fpga': str,   //-- FPGA name
           'size': str,   //-- FPGA size
           'type': str,   //-- FPGA type
           'pack': str,   //-- FPGA packaging
           'verbose': dict  //-- Verbose level
           'top-module`: str  //-- Top module name
         }
       * Resources: Object for accessing the apio resources
    * OUTPUT:
      * Return a tuple (flags, board, arch)
        - flags: A list of strings with the flags valures:
          ['fpga_arch=ice40', 'fpga_size=8k', 'fpga_type=hx',
          fpga_pack='tq144:4k']...
        - board: Board name ('alhambra-ii', 'icezum'...)
        - arch: FPGA architecture ('ice40', 'ecp5'...)
    """

    # -- Current configuration
    # -- Initially it is the default project configuration
    config = {
        BOARD: None,
        FPGA: None,
        ARCH: None,
        TYPE: None,
        SIZE: None,
        PACK: None,
        IDCODE: None,
        VERBOSE: {ALL: False, "yosys": False, "pnr": False},
        TOP_MODULE: None,
        TESTBENCH: None,
    }

    # -- Merge the initial configuration to the current configuration
    config.update(config_ini)

    # -- Read the apio project file (apio.ini)
    proj = Project()
    proj.read()

    # -- proj.board:
    # --   * None: No apio.ini file
    # --   * "name": Board name (str)

    # -- proj.top_module:
    # --  * None: Not specified in apio.ini file
    # --  * "name": name of the top-module to use
    # -- (if not overriden by arguments)

    # -- DEBUG: Print both: project board and configuration board
    # debug_config_item(config, BOARD, proj.board)

    # -- Board name given in the command line
    if config[BOARD]:

        # -- If there is a project file (apio.ini) the board
        # -- given by command line overrides it
        # -- (command line has the highest priority)
        if proj.board:

            # -- As the command line has more priority, and the board
            # -- given in args is different than the one in the project,
            # -- inform the user
            if config[BOARD] != proj.board:
                click.secho("Info: ignore apio.ini board", fg="yellow")

    # -- Board name given in the project file
    else:
        # -- ...read it from the apio.ini file
        config[BOARD] = proj.board

    # -- The board is given (either by arguments or by project file)
    if config[BOARD]:

        # -- First, check if the board is valid
        # -- If not, exit
        if config[BOARD] not in resources.boards:
            raise ValueError(f"unknown board: {config[BOARD]}")

        # -- Read the FPGA name for the current board
        fpga = resources.boards.get(config[BOARD]).get(FPGA)

        # -- Add it to the current configuration
        update_config_item(config, FPGA, fpga)

    # -- Check that the FPGA was given
    if not config[FPGA]:
        perror_insuficient_arguments()
        raise ValueError("Missing FPGA")

    # -- Check if the FPGA is valid
    # -- If not, exit
    if config[FPGA] not in resources.fpgas:
        raise ValueError(f"unknown FPGA: {config[FPGA]}")

    # -- Update the FPGA items according to the current board and fpga
    # -- Raise an exception in case of a contradiction
    # -- For example: board = icezum, and size='8k' given by arguments
    # -- (The board determine the fpga and the size, but the user has
    # --  specificied a different size. It is a contradiction!)
    for item in [ARCH, TYPE, SIZE, PACK, IDCODE]:
        update_config_fpga_item(config, item, resources)

    # -- We already have a final configuration
    # -- Check that this configuration is ok
    # -- At least it should have fpga, type, size and pack
    # -- Exit if it is not correct
    for item in [TYPE, SIZE, PACK]:

        # -- Config item not defined!! it is mandatory!
        if not config[item]:
            perror_insuficient_arguments()
            raise ValueError(f"Missing FPGA {item.upper()}")

    # -- Process the top-module
    # -- Priority 1: Given by arguments in the command line
    # -- If it has not been set by arguments...
    if not config[TOP_MODULE]:

        # -- Priority 2: Use the top module in the apio.ini file
        # -- if it exists...
        if proj.top_module:
            config[TOP_MODULE] = proj.top_module

        # -- NO top-module specified!! Warn the user
        else:
            click.secho(
                "No top module given\n",
                fg="red",
            )
            click.secho(
                "Option 1: Pass it as a parameter\n"
                "   `--top-module <top module name>`\n\n"
                "Option 2: Insert in the ini file\n"
                "   `apio init --top-module <top-module>`\n",
                fg="yellow",
            )

            # -- "main" is used as a default top-level
            config[TOP_MODULE] = "main"

            click.secho("Using the default top-module: `main`", fg="blue")

    # -- Debug: Print current configuration
    # print_configuration(config)

    # -- Build Scons flag list
    flags = serialize_scons_flags(
        {
            "fpga_arch": config[ARCH],
            "fpga_size": config[SIZE],
            "fpga_type": config[TYPE],
            "fpga_pack": config[PACK],
            "fpga_idcode": config[IDCODE],
            "verbose_all": config[VERBOSE][ALL],
            # These two flags appear only in some of the commands.
            "verbose_yosys": (
                config[VERBOSE][YOSYS] if YOSYS in config[VERBOSE] else False
            ),
            "verbose_pnr": (
                config[VERBOSE][PNR] if PNR in config[VERBOSE] else False
            ),
            "top_module": config[TOP_MODULE],
            "testbench": config[TESTBENCH],
        }
    )

    return flags, config[BOARD], config[ARCH]


def update_config_fpga_item(config, item, resources):
    """Update an item for the current FPGA configuration, if there is no
    contradiction.
    It raises an exception in case of contradiction: the current FPGA item
    in the configuration has already a value, but another has been specified
    * INPUTS:
      * Config: Current configuration
      * item: FPGA item to update: ARCH, TYPE, SIZE, PACK, IDCODE
      * value: New valur for the FPGA item, if there is no contradiction
    """

    # -- Read the FPGA item from the apio resources
    fpga_item = resources.fpgas.get(config[FPGA]).get(item)

    # -- Update the current configuration with that item
    # -- and check that there are no contradictions
    update_config_item(config, item, fpga_item)


def update_config_item(config: dict, item: str, value: str) -> None:
    """Update the value of the configuration item, if there is no contradiction
    It raises an exception in case of contradiction: the current item in the
    configuration has one value (ex. size='1k') but another has been specified
    * INPUTS:
      * Config: Current configuration
      * item: Item to update (key): BOARD, ARCH,TYPE, SIZE...
      * value: New value for the item, if there are no contradictions
    """

    # -- Debug messages
    # debug_config_item(config, item, value)

    # -- This item has not been set in the current configuration: ok, set it!
    if config[item] is None:
        config[item] = value

    # -- That item already has a value... and another difffernt is being
    # -- given.. This is a contradiction!!!
    else:
        # -- It is a contradiction if their names are different
        # -- When the name is the same, it is redundant...
        # -- but it is not a problem
        if value != config[item]:
            raise ValueError(f"contradictory arguments: {value, config[item]}")


def debug_config_item(config: dict, item: str, value: str) -> None:
    """Print a Debug message related to the project configuration
    INPUTS:
      * config: Current configuration
      * item: item name to print. It is a key of the configuration:
        BOARD, ARCH, TYPE, SIZE, PACK, IDCODE....
      * Value: Value of that item specified in the project
    """
    print(f"(Debug): {item}, Project: {value}, Argument: {config[item]}")


def print_configuration(config: dict) -> None:
    """DEBUG function: Print the current configuration on the
    console
      * INPUTS:
        * configuration: Current project configuration
    """
    print()
    print("(Debug): Current configuration:")
    print("  ITEM:  VALUE")
    print("  ----   -----")
    print(f"  board: {config[BOARD]}")
    print(f"  fpga: {config[FPGA]}")
    print(f"  arch: {config[ARCH]}")
    print(f"  type: {config[TYPE]}")
    print(f"  size: {config[SIZE]}")
    print(f"  pack: {config[PACK]}")
    print(f"  idcode: {config[IDCODE]}")
    print(f"  top-module: {config[TOP_MODULE]}")
    print(f"  testbench: {config[TESTBENCH]}")
    print("  verbose:")
    print(f"    all: {config[VERBOSE][ALL]}")
    # These two flags appear only in some of the commands.
    if YOSYS in config[VERBOSE]:
        print(f"    yosys: {config[VERBOSE][YOSYS]}")
    if PNR in config[VERBOSE]:
        print(f"    pnr: {config[VERBOSE][PNR]}")
    print()


def perror_insuficient_arguments():
    """Print an error: not enough arguments given"""

    click.secho(
        "Error: insufficient arguments: missing board",
        fg="red",
    )
    click.secho(
        "You have two options:\n"
        "  1) Execute your command with\n"
        "       `--board <boardname>`\n"
        "  2) Create an ini file using\n"
        "       `apio init --board <boardname>`",
        fg="yellow",
    )


def serialize_scons_flags(flags: dict) -> list:
    """Format the scons flags as a list of string of
    the form: 'flag=value'
    """

    # -- Create and empty list
    flag_list = []

    # -- Read all the flags
    for key, value in flags.items():

        # -- Append to the list only the flags with value
        if value:
            flag_list.append(f"{key}={value}")

    # -- Return the list
    return flag_list
