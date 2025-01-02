# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- Licence GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- Licence Apache v2
"""Provides access to the apio scons args."""


# -- Per https://stackoverflow.com/a/33533514/15038713.
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List
import os
import sys
from click import secho


# pylint: disable=invalid-name
# pylint: disable=too-many-instance-attributes


class ApioArgsParser:
    """A helper class for parsing apio scons args."""

    def __init__(self, scons_args: Dict[str, str], is_debug: bool):
        self.scons_args = scons_args
        self.is_debug = is_debug
        # -- A set to track ignored args.
        self._parsed_args = set()

    def _dump_parsed_arg(self, name, value) -> None:
        """Used to dump parsed scons arg. For debugging only."""
        if self.is_debug:
            type_name = type(value).__name__
            secho(f"Arg  {name:15} ->  {type_name:6}  {str(value)}")

    def arg_str(self, name: str) -> str:
        """Parse and return a string arg."""
        value = self.scons_args.get(name, "")
        self._dump_parsed_arg(name, value)
        self._parsed_args.add(name)
        return value

    def arg_bool(self, name: str) -> bool:
        """Parse and return a boolean arg."""
        raw_value = self.scons_args.get(name, "False")
        value = {"True": True, "False": False, True: True, False: False}[
            raw_value
        ]
        assert value is not None, f"Invalid bool'{name} = '{raw_value}'."
        self._dump_parsed_arg(name, value)
        self._parsed_args.add(name)
        return value

    def env_str(self, name: str) -> str:
        """Get an os env required value.."""
        value = os.environ[name]
        assert (
            value is not None
        ), f"Error: missing required apio scons env var '{name}'."
        self._dump_parsed_arg(name, value)
        return value

    def check_all_args_parsed(self) -> None:
        """Check that all scons args were parsed. Fatal error if not."""
        ignored = [x for x in self.scons_args if x not in self._parsed_args]
        if ignored:
            secho(
                f"Error: Unknown scons args: {', '.join(ignored)}",
                fg="red",
                color=True,
            )
            sys.exit(1)


@dataclass(frozen=True)
class ApioArgs:
    """Apio scons args values. Contains values from scons args and os env."""

    # -- Scons str args.
    PROG: str
    PLATFORM_ID: str
    FPGA_ARCH: str
    FPGA_MODEL: str
    FPGA_SIZE: str
    FPGA_TYPE: str
    FPGA_PACK: str
    TOP_MODULE: str
    FPGA_IDCODE: str
    TESTBENCH: str
    VERILATOR_NOWARNS: List[str]
    VERILATOR_WARNS: List[str]
    GRAPH_SPEC: str

    # -- Scons bool args.
    VERBOSE_ALL: bool
    VERBOSE_YOSYS: bool
    VERBOSE_PNR: bool
    FORCE_SIM: bool
    VERILATOR_ALL: bool
    VERILATOR_NO_STYLE: bool

    # -- Env str vars.
    YOSYS_PATH: str
    TRELLIS_PATH: str

    def __post_init__(self):
        """Post __init__() sanity check."""
        # -- Check required values.
        assert self.PLATFORM_ID
        assert self.YOSYS_PATH
        assert self.TRELLIS_PATH

    @classmethod
    def make(cls, scons_args: Dict[str, str], is_debug: bool) -> ApioArgs:
        """Return a ApioArgs object with the parsed args."""
        parser = ApioArgsParser(scons_args, is_debug)

        result = ApioArgs(
            # Scons tring args.
            PROG=parser.arg_str("prog"),
            PLATFORM_ID=parser.arg_str("platform_id"),
            FPGA_ARCH=parser.arg_str("fpga_arch"),
            FPGA_MODEL=parser.arg_str("fpga_model"),
            FPGA_SIZE=parser.arg_str("fpga_size"),
            FPGA_TYPE=parser.arg_str("fpga_type"),
            FPGA_PACK=parser.arg_str("fpga_pack"),
            TOP_MODULE=parser.arg_str("top_module"),
            FPGA_IDCODE=parser.arg_str("fpga_idcode"),
            TESTBENCH=parser.arg_str("testbench"),
            VERILATOR_NOWARNS=parser.arg_str("nowarn").split(","),
            VERILATOR_WARNS=parser.arg_str("warn").split(","),
            GRAPH_SPEC=parser.arg_str("graph_spec"),
            # Scons bool args
            VERBOSE_ALL=parser.arg_bool("verbose_all"),
            VERBOSE_YOSYS=parser.arg_bool("verbose_yosys"),
            VERBOSE_PNR=parser.arg_bool("verbose_pnr"),
            FORCE_SIM=parser.arg_bool("force_sim"),
            VERILATOR_ALL=parser.arg_bool("all"),
            VERILATOR_NO_STYLE=parser.arg_bool("nostyle"),
            # Env str vars.
            YOSYS_PATH=parser.env_str("YOSYS_LIB"),
            TRELLIS_PATH=parser.env_str("TRELLIS"),
        )

        # -- Check that all args were parsed.
        parser.check_all_args_parsed()

        return result
