# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Utilities for procesing the arguments passed to apio commands"""


import traceback
from functools import wraps
from typing import Dict, Tuple, Optional, List, Any
import click
from apio.managers.project import DEFAULT_TOP_MODULE
from apio.apio_context import ApioContext


# -- Names of supported args. Unless specified otherwise, all args are optional
# -- and have a string value. Values such as None, "", or False, which
# -- evaluate to a boolean False are considered 'no value' and are ignored.
ARG_BOARD_ID = "board"
ARG_FPGA_ID = "fpga"
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
ARG_FORCE_SIM = "force_sim"  # Bool
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

        # -- Call the function, dump exceptions, if any.
        try:
            result = process_arguments_func(*args)

        except Exception:
            print(traceback.format_exc())
            raise

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


class Arg:
    """Represent an arg."""

    def __init__(self, arg_name: str, var_name: str = None):
        """If var_name exists, the arg is mapped to scons varialbe with
        that name."""
        self._name: str = arg_name
        self._var_name: Optional[str] = var_name
        self._has_value: bool = False
        self._value: Any = None

    def __repr__(self):
        """Object representation, for debugging."""
        result = f"Arg '{self._name}'"
        if self._has_value:
            result += f" = {self._value.__repr__()}"
        else:
            result += " (no value)"
        return result

    @property
    def name(self):
        """Returns the arg name."""
        return self._name

    @property
    def has_value(self):
        """True if a value was set."""
        return self._has_value

    def set(self, value: Any):
        """Sets a value.  Value cannot be None, "", False, or any other value
        that is evaluated to a bool False. Value can be set only once, unless
        if writing the same value."""
        # -- These are programming errors, not user error.
        assert value, f"Setting arg '{self._name}' with a None value."
        if not self._has_value:
            self._value = value
            self._has_value = True
        elif value != self._value:
            raise ValueError(
                f"contradictory argument values: "
                f"'{self._name}' = ({value} vs {self._value})"
            )

    @property
    def value(self):
        """Returns the value. hould be called only if has_value is True."""
        assert self._has_value, f"Arg '{self._name}' has no value to read."
        return self._value

    def value_or(self, default):
        """Returns value or default if no value."""
        if self._has_value:
            return self._value
        return default

    @property
    def has_var_value(self):
        """Does the arg contain a value that should be exported as a scons
        variable? To qualify, it needs to has a var name and a value.
        To qualify, it needs to"""
        return self._var_name and self._has_value

    @property
    def var_name(self):
        """Returns the name of the scons variable. Should be called only
        if the arg is known to have a variable name."""
        assert (
            self._var_name is not None
        ), f"Arg '{self._name}' has no var arg."
        return self._var_name


# R0912: Too many branches (14/12)
# pylint: disable=R0912
#
# -- Uncomment the decoracotor below for debugging.
# @debug_dump
def process_arguments(
    apio_ctx: ApioContext, seed_args: Dict
) -> Tuple[List[str], str, Optional[str]]:
    """Construct the scons variables list from an ApioContext and user
    provided scons args.  The list of the valid entires in the args ditct,
    see ARG_XX definitions above.

       * apio_ctx: ApioContext of this apio invocation. Should be created with
         'load_project'  = True.
       * args: a Dictionary with the scons args.
    * OUTPUT:
      * Return a tuple (variables, board, arch)
        - variables: A list of strings scons variables. For example
          ['fpga_arch=ice40', 'fpga_size=8k', 'fpga_type=hx',
          fpga_pack='tq144:4k']...
        - board: Board name ('alhambra-ii', 'icezum'...)
        - arch: FPGA architecture ('ice40', 'ecp5'...)
    """

    # -- We expect here only contexts at project scope. Currently apio.ini
    # -- is still not required so apio_ctx.project can still be None.
    assert (
        apio_ctx.project_loading_requested
    ), "Apio context not at project scope."

    # -- Construct the args dictionary with all supported args. Most of the
    # -- args also have the name of their exported scons variable.
    args: Dict[str, Arg] = {
        ARG_BOARD_ID: Arg(ARG_BOARD_ID),
        ARG_FPGA_ID: Arg(ARG_FPGA_ID, "fpga_model"),
        ARG_FPGA_ARCH: Arg(ARG_FPGA_ARCH, "fpga_arch"),
        ARG_FPGA_TYPE: Arg(ARG_FPGA_TYPE, "fpga_type"),
        ARG_FPGA_SIZE: Arg(ARG_FPGA_SIZE, "fpga_size"),
        ARG_FPGA_PACK: Arg(ARG_FPGA_PACK, "fpga_pack"),
        ARG_FPGA_IDCODE: Arg(ARG_FPGA_IDCODE, "fpga_idcode"),
        ARG_VERBOSE_ALL: Arg(ARG_VERBOSE_ALL, "verbose_all"),
        ARG_VERBOSE_YOSYS: Arg(ARG_VERBOSE_YOSYS, "verbose_yosys"),
        ARG_VERBOSE_PNR: Arg(ARG_VERBOSE_PNR, "verbose_pnr"),
        ARG_TOP_MODULE: Arg(ARG_TOP_MODULE, "top_module"),
        ARG_TESTBENCH: Arg(ARG_TESTBENCH, "testbench"),
        ARG_FORCE_SIM: Arg(ARG_FORCE_SIM, "force_sim"),
        ARG_GRAPH_SPEC: Arg(ARG_GRAPH_SPEC, "graph_spec"),
        ARG_PLATFORM_ID: Arg(ARG_PLATFORM_ID, "platform_id"),
        ARG_VERILATOR_ALL: Arg(ARG_VERILATOR_ALL, "all"),
        ARG_VERILATOR_NO_STYLE: Arg(ARG_VERILATOR_NO_STYLE, "nostyle"),
        ARG_VERILATOR_NO_WARN: Arg(ARG_VERILATOR_NO_WARN, "nowarn"),
        ARG_VERILATOR_WARN: Arg(ARG_VERILATOR_WARN, "warn"),
    }

    # -- Populate a subset of the args from the seed. We ignore values such as
    # -- None, "", 0, and False which evaluate to boolean False. We expect
    # -- those to be the default at the SConstruct arg parsing.
    for arg_name, seed_value in seed_args.items():
        if seed_value:
            args[arg_name].set(seed_value)

    # -- Keep a shortcut, for convinience. Note that project can be None
    # -- if the project doesn't have a apio.ini file.
    project = apio_ctx.project

    # -- Board name given in the command line
    if args[ARG_BOARD_ID].has_value:

        # -- If there is a project file (apio.ini) the board
        # -- given by command line overrides it
        # -- (command line has the highest priority)
        if project and project["board"]:

            # -- As the command line has more priority, and the board
            # -- given in args is different than the one in the project,
            # -- inform the user
            if args[ARG_BOARD_ID].value != project["board"]:
                click.secho(
                    "Info: ignoring board specification from apio.ini.",
                    fg="yellow",
                )

    # -- Try getting the board id from the project
    else:
        # -- ...read it from the apio.ini file
        if project and project["board"]:
            args[ARG_BOARD_ID].set(project["board"])

            # update_arg(args, ARG_BOARD, project.board)

    # -- The board is given (either by arguments or by project file)
    if args[ARG_BOARD_ID].has_value:

        # -- Check that the board id is valid.
        if args[ARG_BOARD_ID].value not in apio_ctx.boards:
            raise ValueError(f"unknown board: {args[ARG_BOARD_ID].value}")

        # -- Read the FPGA name for the current board
        fpga = apio_ctx.boards.get(args[ARG_BOARD_ID].value).get(ARG_FPGA_ID)

        # -- Add it to the current configuration
        if fpga:
            args[ARG_FPGA_ID].set(fpga)

    # -- Check that the FPGA was given
    if not args[ARG_FPGA_ID].has_value:
        perror_insuficient_arguments()
        raise ValueError("Missing FPGA")

    # -- Check that the FPGA is valid
    if args[ARG_FPGA_ID].value not in apio_ctx.fpgas:
        raise ValueError(f"unknown FPGA: {args[ARG_FPGA_ID].value}")

    # -- Update the FPGA items according to the current board and fpga
    # -- Raise an exception in case of a contradiction
    # -- For example: board = icezum, and size='8k' given by arguments
    # -- (The board determine the fpga and the size, but the user has
    # --  specificied a different size. It is a contradiction!)
    for arg, fpga_property_name in [
        [args[ARG_FPGA_ARCH], "arch"],
        [args[ARG_FPGA_TYPE], "type"],
        [args[ARG_FPGA_SIZE], "size"],
        [args[ARG_FPGA_PACK], "pack"],
        [args[ARG_FPGA_IDCODE], "idcode"],
    ]:
        # -- Get the fpga property, if exits.
        fpga_config = apio_ctx.fpgas.get(args[ARG_FPGA_ID].value)
        fpga_property = fpga_config.get(fpga_property_name, None)

        if fpga_property:
            arg.set(fpga_property)

    # -- We already have a final configuration
    # -- Check that this configuration is ok
    # -- At least it should have fpga, type, size and pack
    # -- Exit if it is not correct
    for arg in [args[ARG_FPGA_TYPE], args[ARG_FPGA_SIZE], args[ARG_FPGA_PACK]]:

        # -- Config item not defined!! it is mandatory!
        if not arg.has_value:
            perror_insuficient_arguments()
            raise ValueError(f"Missing FPGA {arg.name.upper()}")

    # -- If top-module not specified by the user, determine what value to use.
    if not args[ARG_TOP_MODULE].has_value:

        if project and project["top-module"]:
            # -- If apio.ini has a top-module value use it.

            args[ARG_TOP_MODULE].set(project["top-module"])
        else:

            # -- Use the default top-level
            args[ARG_TOP_MODULE].set(DEFAULT_TOP_MODULE)

            click.secho(
                "Warning: 'top-module' is not specified in apio.ini, "
                f"assuming: '{DEFAULT_TOP_MODULE}'",
                fg="yellow",
            )

    # -- Set the platform id.
    assert apio_ctx.platform_id, "Missing platform_id in apio context"
    args[ARG_PLATFORM_ID].set(apio_ctx.platform_id)

    # -- Construct the vars list we send to the scons process.
    # -- We ignore values such as None, "", 0, and False which evaluate
    # -- to boolean False. We expect those to be the default at the
    # -- SConstruct arg parsing.
    variables = []
    for arg in args.values():
        if arg.has_var_value:
            variables.append(f"{arg.var_name}={arg.value}")

    # -- All done.
    return (
        variables,
        args[ARG_BOARD_ID].value_or(None),
        args[ARG_FPGA_ARCH].value_or(None),
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
