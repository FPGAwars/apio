# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Utilities for procesing the arguments passed to apio commands"""

# pylint: disable=fixme
# TODO: Instead of costructing args and then mapping it to
# variables_dict and filtering variables dict, , it would be
# more straight forward to directly constructing the filtered
# variables dict.

from functools import wraps
from typing import Dict, Tuple, Optional, List
import click
from apio.managers.project import Project, DEFAULT_TOP_MODULE
from apio.apio_context import ApioContext


# -- Names of supported keys in the input process_arguments' args dict.
# -- Unless specified otherwise, all values are strings and optional (that is,
# -- can not exist in 'args' or have a None or empty value).
ARG_BOARD = "board"  # Required.
ARG_FPGA_ID = "fpga"  # Required, ids per fpgas.json.
ARG_FPGA_ARCH = "arch"
ARG_FPGA_TYPE = "type"
ARG_FPGA_SIZE = "size"
ARG_FPGA_PACK = "pack"
ARG_FPGA_IDCODE = "idcode"
ARG_VERBOSE_ALL = "verbose_all"  # Bool.
ARG_VERBOSE_YOSYS = "verbose_yosys"  # Bool
ARG_VERBOSE_PNR = "verbose_pnr"  # Bool
ARG_TOP_MODULE = "top-module"
ARG_TESTBENCH = "testbench"
ARG_GRAPH_SPEC = "graph_spec"
ARG_PLATFORM_ID = "platform_id"
ARG_VERILATOR_ALL = "all"
ARG_VERILATOR_NO_STYLE = "nostyle"
ARG_VERILATOR_NO_WARN = "nowarn"
ARG_VERILATOR_WARN = "warn"


def debug_dump(process_arguments_func):
    """A decorator for debugging. It prints the input and output of
    process_arguments(). Comment out the '@debug_dump' statement
    below to enable, comment to disable..

    INPUTS:
      * fun: Function to DEBUG
    """

    @wraps(process_arguments_func)
    def outer(*args):

        # -- Print the arguments
        print(
            f"--> DEBUG!. Function {process_arguments_func.__name__}(). BEGIN"
        )
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
        result = process_arguments_func(*args)

        # -- Print its output
        print(f"--> DEBUG!. Function {process_arguments_func.__name__}(). END")
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
#
# -- Uncomment the decoracotor below for debugging.
# @debug_dump
def process_arguments(
    apio_ctx: ApioContext, seed_args: Dict, project: Project
) -> Tuple[List[str], str, Optional[str]]:
    """Construct the scons variables list from an ApioContext and user
    provided scons args.  The list of the valid entires in the args ditct,
    see ARG_XX definitions above.

       * apio_ctx: ApioContext of this apio invocation.
       * args: a Dictionary with the scons args.
       * Project: Optional project information.
    * OUTPUT:
      * Return a tuple (variables, board, arch)
        - variables: A list of strings scons variables. For example
          ['fpga_arch=ice40', 'fpga_size=8k', 'fpga_type=hx',
          fpga_pack='tq144:4k']...
        - board: Board name ('alhambra-ii', 'icezum'...)
        - arch: FPGA architecture ('ice40', 'ecp5'...)
    """

    # -- We will populate a new set of args from input args and other values
    # -- we pull from the apio context.
    args = {
        ARG_BOARD: None,
        ARG_FPGA_ID: None,
        ARG_FPGA_ARCH: None,
        ARG_FPGA_TYPE: None,
        ARG_FPGA_SIZE: None,
        ARG_FPGA_PACK: None,
        ARG_FPGA_IDCODE: None,
        ARG_VERBOSE_ALL: None,
        ARG_VERBOSE_YOSYS: None,
        ARG_VERBOSE_PNR: None,
        ARG_TOP_MODULE: None,
        ARG_TESTBENCH: None,
        ARG_GRAPH_SPEC: None,
        ARG_PLATFORM_ID: None,
        ARG_VERILATOR_ALL: None,
        ARG_VERILATOR_NO_STYLE: None,
        ARG_VERILATOR_NO_WARN: None,
        ARG_VERILATOR_WARN: None,
    }

    # -- We expect args to contain all the supported args and we expect seed
    # -- args to contain a subset of those. A failure here indicates a
    # -- programming error.
    unknown_args = [x for x in seed_args.keys() if x not in args]
    assert len(unknown_args) == 0, f"Unexpected sconsargs: {unknown_args}"

    # -- Merge the initial configuration to the current configuration
    args.update(seed_args)

    # -- Board name given in the command line
    if args[ARG_BOARD]:

        # -- If there is a project file (apio.ini) the board
        # -- given by command line overrides it
        # -- (command line has the highest priority)
        if project.board:

            # -- As the command line has more priority, and the board
            # -- given in args is different than the one in the project,
            # -- inform the user
            if args[ARG_BOARD] != project.board:
                click.secho(
                    "Info: ignoring board specification from apio.ini.",
                    fg="yellow",
                )

    # -- Board name given in the project file
    else:
        # -- ...read it from the apio.ini file
        if project.board:
            update_arg(args, ARG_BOARD, project.board)

    # -- The board is given (either by arguments or by project file)
    if args[ARG_BOARD]:

        # -- First, check if the board is valid
        # -- If not, exit
        if args[ARG_BOARD] not in apio_ctx.boards:
            raise ValueError(f"unknown board: {args[ARG_BOARD]}")

        # -- Read the FPGA name for the current board
        fpga = apio_ctx.boards.get(args[ARG_BOARD]).get(ARG_FPGA_ID)

        # -- Add it to the current configuration
        if fpga:
            update_arg(args, ARG_FPGA_ID, fpga)

    # -- Check that the FPGA was given
    if not args[ARG_FPGA_ID]:
        perror_insuficient_arguments()
        raise ValueError("Missing FPGA")

    # -- Check if the FPGA is valid
    # -- If not, exit
    if args[ARG_FPGA_ID] not in apio_ctx.fpgas:
        raise ValueError(f"unknown FPGA: {args[ARG_FPGA_ID]}")

    # -- Update the FPGA items according to the current board and fpga
    # -- Raise an exception in case of a contradiction
    # -- For example: board = icezum, and size='8k' given by arguments
    # -- (The board determine the fpga and the size, but the user has
    # --  specificied a different size. It is a contradiction!)
    for arg_name, fpga_property in [
        [ARG_FPGA_ARCH, "arch"],
        [ARG_FPGA_TYPE, "type"],
        [ARG_FPGA_SIZE, "size"],
        [ARG_FPGA_PACK, "pack"],
        [ARG_FPGA_IDCODE, "idcode"],
    ]:
        _update_fpga_property_arg(apio_ctx, args, arg_name, fpga_property)

    # -- We already have a final configuration
    # -- Check that this configuration is ok
    # -- At least it should have fpga, type, size and pack
    # -- Exit if it is not correct
    for arg_name in [ARG_FPGA_TYPE, ARG_FPGA_SIZE, ARG_FPGA_PACK]:

        # -- Config item not defined!! it is mandatory!
        if not args[arg_name]:
            perror_insuficient_arguments()
            raise ValueError(f"Missing FPGA {arg_name.upper()}")

    # -- Process the top-module
    # -- Priority 1: Given by arguments in the command line
    # -- If it has not been set by arguments...
    if not args[ARG_TOP_MODULE]:

        # -- Priority 2: Use the top module in the apio.ini file
        # -- if it exists...
        if project.top_module:
            update_arg(args, ARG_TOP_MODULE, project.top_module)

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
                "   `apio modify --top-module <top-module>`\n",
                fg="yellow",
            )

            # -- Use the default top-level
            update_arg(args, ARG_TOP_MODULE, DEFAULT_TOP_MODULE)

            click.secho(
                f"Using the default top-module: `{DEFAULT_TOP_MODULE}`",
                fg="blue",
            )

    # -- Set the platform id.
    update_arg(args, ARG_PLATFORM_ID, apio_ctx.platform_id)

    # -- Build Scons flag list. This is a differnet set of names that may
    # -- be different from the args set of names. These keys should match
    # -- the arg keys at the begining of the SConstruct files.
    variables_dict = {
        "fpga_model": args[ARG_FPGA_ID],
        "fpga_arch": args[ARG_FPGA_ARCH],
        "fpga_size": args[ARG_FPGA_SIZE],
        "fpga_type": args[ARG_FPGA_TYPE],
        "fpga_pack": args[ARG_FPGA_PACK],
        "fpga_idcode": args[ARG_FPGA_IDCODE],
        "verbose_all": args[ARG_VERBOSE_ALL],
        "verbose_yosys": args[ARG_VERBOSE_YOSYS],
        "verbose_pnr": args[ARG_VERBOSE_PNR],
        "top_module": args[ARG_TOP_MODULE],
        "testbench": args[ARG_TESTBENCH],
        "graph_spec": args[ARG_GRAPH_SPEC],
        "platform_id": args[ARG_PLATFORM_ID],
        "all": args[ARG_VERILATOR_ALL],
        "nostyle": args[ARG_VERILATOR_NO_STYLE],
        "nowarn": args[ARG_VERILATOR_NO_WARN],
        "warn": args[ARG_VERILATOR_WARN],
    }

    # -- Convert to a list of 'name=value' strings. Entires with
    # -- bool(value) == False are skipped.
    variables = serialize_scons_variables(variables_dict)

    # -- All done.
    return variables, args[ARG_BOARD], args[ARG_FPGA_ARCH]


def _update_fpga_property_arg(
    apio_ctx: ApioContext, args, arg_name, fpga_property_name
):
    """Update an fpga property in the given args dictionary.

    It raises an exception if the there are differnet values in the args
    dictionary and the fpga property.

    It assumes that args already contains the FPGA id arg.

    * INPUTS:
      * Apio_ctx: the context of this apio invocation.
      * args: the args dictionary to populate.
      * arg_name: the arg name in the dictionary
      * fpga_property: the matching property name in fpgas.json.
    """

    # -- Get the fpga definition.
    fpga_config = apio_ctx.fpgas.get(args[ARG_FPGA_ID])

    # -- Get the fpga property value, if exists.
    fpga_property_value = fpga_config.get(fpga_property_name, None)

    # -- Update the arg in args, error if the value conflicts.
    if fpga_property_value:
        update_arg(args, arg_name, fpga_property_value)


def update_arg(args: dict, arg_name: str, new_value: str) -> None:
    """Update the a value in the args dict. If arg_name doesn't exist
    in args or if it has a non None value that is different from new_value
    than an exception is thrown.
    * INPUTS:
      * args: A dictionary with the args.
      * arg_name: The arg name, e.g. ARG_BOARD.
      * value: New value for the arg. Can't be None.
    """
    # -- Sanity checks. These are all programming errors.
    assert arg_name in args, f"Unknown arg: {arg_name}"
    assert new_value is not None, f"Trying to set {arg_name} = None"

    # -- Get the old value. May be None.
    old_value = args[arg_name]

    # -- If no old value then set the new value.
    if old_value is None:
        args[arg_name] = new_value
        return

    # -- If new value is same as old value, do nothing.
    if old_value == new_value:
        return

    # -- Having conflicting values.
    raise ValueError(
        f"contradictory argument values: "
        f"'{arg_name}' = ({new_value} vs {old_value})"
    )


def perror_insuficient_arguments():
    """Print an error: not enough arguments given"""

    click.secho(
        "Error: insufficient arguments: missing board",
        fg="red",
    )
    click.secho(
        "You have a few options:\n"
        "  1) Change to a project directory with an apio.ini file\n"
        "  2) Specify the directory of a project with an apio.ini file\n"
        "       `--project-dir <projectdir>\n"
        "  3) Create a project file apio.ini manually or using\n"
        "       `apio create --board <boardname>`\n"
        "  4) Execute your command with the flag\n"
        "       `--board <boardname>`",
        fg="yellow",
    )


def serialize_scons_variables(flags: dict) -> list:
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
