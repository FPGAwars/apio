# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2019 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
"""Utilities for procesing the arguments passed to apio commands"""


from typing import Dict, Tuple, Optional, List, Any
from apio.apio_context import ApioContext
from apio.utils import util


# -- Names of supported args. Unless specified otherwise, all args are optional
# -- and have a string value. Values such as None, "", or False, which
# -- evaluate to a boolean False are considered 'no value' and are ignored.
ARG_FPGA_PART_NUM = "part_num"
ARG_FPGA_ARCH = "arch"
ARG_FPGA_TYPE = "type"
ARG_FPGA_PACK = "pack"
ARG_FPGA_SPEED = "speed"
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
ARG_DEBUG = "debug"


class Arg:
    """Represent an arg."""

    def __init__(self, arg_name: str, var_name: str):
        """The arg is mapped from arg_name to to scons varialbe var_name."""
        assert isinstance(arg_name, str)
        assert isinstance(var_name, str)
        self.arg_name: str = arg_name
        self.var_name: Optional[str] = var_name
        self.has_value: bool = False
        self._value: Any = None

    def __repr__(self):
        """Object representation, for debugging."""
        result = f"Arg '{self.arg_name}'"
        if self.has_value:
            result += f" = {self._value.__repr__()}"
        else:
            result += " (no value)"
        return result

    def set(self, value: Any):
        """Sets a value.  Value cannot be None, "", False, or any other value
        that is evaluated to a bool False. Value can be set only once, unless
        if writing the same value."""
        # -- These are programming errors, not user error.
        assert (
            value is not None
        ), f"Setting arg '{self.arg_name}' with None value."
        if not self.has_value:
            self._value = value
            self.has_value = True
        elif value != self._value:
            raise ValueError(
                f"contradictory argument values: "
                f"'{self.arg_name}' = ({value} vs {self._value})"
            )

    @property
    def value(self):
        """Returns the value. hould be called only if has_value is True."""
        assert self.has_value, f"Arg '{self.arg_name}' has no value to read."
        return self._value

    def value_or(self, default):
        """Returns value or default if no value."""
        if self.has_value:
            return self._value
        return default


# R0912: Too many branches (14/12)
# pylint: disable=R0912
#
@util.debug_decoractor
def process_arguments(
    apio_ctx: ApioContext, seed_args: Dict
) -> Tuple[str, List[str]]:
    """Construct the scons variables list from an ApioContext and user
    provided scons args.  The list of the valid entires in the args ditct,
    see ARG_XX definitions above.

       * apio_ctx: ApioContext of this apio invocation. Should have the
         project file loaded.
       * args: a Dictionary with the scons args.
    * OUTPUT:
      * Return a tuple (board, variables)
        - board: Board name ('alhambra-ii', 'icezum'...)
        - variables: A list of strings scons variables. For example
          ['fpga_arch=ice40', 'fpga_type=hx',
          fpga_pack='tq144:4k']...
    """

    # -- Construct the args dictionary with all supported args. Most of the
    # -- args also have the name of their exported scons variable.
    args: Dict[str, Arg] = {
        ARG_FPGA_PART_NUM: Arg(ARG_FPGA_PART_NUM, "fpga_part_num"),
        ARG_FPGA_ARCH: Arg(ARG_FPGA_ARCH, "fpga_arch"),
        ARG_FPGA_TYPE: Arg(ARG_FPGA_TYPE, "fpga_type"),
        ARG_FPGA_PACK: Arg(ARG_FPGA_PACK, "fpga_pack"),
        ARG_FPGA_SPEED: Arg(ARG_FPGA_SPEED, "fpga_speed"),
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
        ARG_DEBUG: Arg(ARG_DEBUG, "debug"),
    }

    # -- Populate a subset of the args from the seed. We ignore values such as
    # -- None, "", 0, and False which evaluate to boolean False. We expect
    # -- those to be the default at the SConstruct arg parsing.
    for arg_name, seed_value in seed_args.items():
        if seed_value:
            args[arg_name].set(seed_value)

    # -- Get the project object. All commands that invoke scons are expected
    # -- to be in a project context.
    assert apio_ctx.has_project, "Scons encountered a missing project."
    project = apio_ctx.project

    # -- Get project's board. It should be prevalidated when loading the
    # -- project, but we sanity check it again just in case.
    board = project["board"]
    assert board is not None, "Scons got a None board."
    assert board in apio_ctx.boards, f"Unknown board name [{board}]"

    # -- Get the fpga id from the board. This is a required field.
    fpga_id = apio_ctx.boards.get(board).get("fpga")
    assert fpga_id, "process_arguments(): fpga assertion failed."
    assert (
        fpga_id in apio_ctx.fpgas
    ), f"process_arguments(): unknown fpga {fpga_id} "

    # -- Populate the fpga args from the fpga config. We check later, at
    # -- the architecture plugin level that the required values for that
    # -- plugin exit.
    for arg, fpga_property_name in [
        [args[ARG_FPGA_PART_NUM], "part_num"],
        [args[ARG_FPGA_ARCH], "arch"],
        [args[ARG_FPGA_TYPE], "type"],
        [args[ARG_FPGA_PACK], "pack"],
        [args[ARG_FPGA_SPEED], "speed"],
    ]:
        # -- Get the fpga property, if exits.
        fpga_config = apio_ctx.fpgas.get(fpga_id)
        fpga_property = fpga_config.get(fpga_property_name, None)

        # -- Populate the arg if the field has a non default value.
        if fpga_property:
            arg.set(fpga_property)

    # -- If top-module not specified by the user (e.g. for apio graph command),
    # -- use the top module from the project file.
    if not args[ARG_TOP_MODULE].has_value:
        args[ARG_TOP_MODULE].set(project["top-module"])

    # -- Set the platform id.
    assert apio_ctx.platform_id, "Missing platform_id in apio context"
    args[ARG_PLATFORM_ID].set(apio_ctx.platform_id)

    # -- Set the debug flag.
    args[ARG_DEBUG].set(util.is_debug())

    # -- Construct the vars list we send to the scons process.
    # -- We ignore values such as None, "", 0, and False which evaluate
    # -- to boolean False. We expect those to be the default at the
    # -- SConstruct arg parsing.
    variables = []
    for arg in args.values():
        if arg.has_value and arg.value:
            variables.append(f"{arg.var_name}={arg.value}")

    # -- All done.
    return (
        board,
        variables,
    )
