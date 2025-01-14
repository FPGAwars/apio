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

    def _maybe_dump_parsed_arg(self, name, value) -> None:
        """Used to dump parsed scons arg. For debugging only."""
        if self.is_debug:
            type_name = type(value).__name__
            secho(f"Arg  {name:15} ->  {type_name:6}  {str(value)}")

    def arg_str(self, name: str) -> str:
        """Parse and return a string arg. Default is ''."""
        value = self.scons_args.get(name, "")
        self._maybe_dump_parsed_arg(name, value)
        self._parsed_args.add(name)
        return value

    def env_str_list(
        self,
        name: str,
        seperator: str,
        *,
        strip: bool = False,
        keep_empty: bool = True,
    ) -> str:
        """Parse and return a string arg that is a sperarated list. Default
        is []."""
        value = self.scons_args.get(name, "")
        # -- Workaround for "".split(",") returning [''].
        value = value.split(seperator) if value else []
        # -- Strip elements if requested.
        if strip:
            value = [x.strip() for x in value]
        # -- Remove empty elements if requested.
        if not keep_empty:
            value = [x for x in value if x]
        # -- Track args parsing.
        self._maybe_dump_parsed_arg(name, value)
        self._parsed_args.add(name)
        # --All done.
        return value

    def arg_bool(self, name: str) -> bool:
        """Parse and return a boolean arg. Default is False."""
        raw_value = self.scons_args.get(name, "False")
        value = {"True": True, "False": False, True: True, False: False}[
            raw_value
        ]
        assert value is not None, f"Invalid bool'{name} = '{raw_value}'."
        self._maybe_dump_parsed_arg(name, value)
        self._parsed_args.add(name)
        return value

    def env_var_str(self, name: str) -> str:
        """Get an os env required value. Default is ''."""
        value = os.getenv(name)
        if value is None:
            value = ""
        self._maybe_dump_parsed_arg(name, value)
        return value

    def check_all_args_parsed(self) -> None:
        """Check that all scons args were parsed. Fatal error if not."""
        ignored = [x for x in self.scons_args if x not in self._parsed_args]
        if ignored:
            secho(
                f"Error: Unknown scons args: {ignored}",
                fg="red",
            )
            sys.exit(1)


@dataclass(frozen=True)
class ApioArgs:
    """Apio scons args values. Contains values from scons args and os env."""

    # -- Scons str args.
    PROG: str
    PLATFORM_ID: str
    FPGA_ARCH: str
    FPGA_PART_NUM: str
    FPGA_TYPE: str
    FPGA_PACK: str
    TOP_MODULE: str
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
        assert self.PLATFORM_ID, "platform_id scons arg is required."
        assert self.YOSYS_PATH, "YOSYS_PATH env var is required."
        assert self.TRELLIS_PATH, "TRELLIS_PATH env var is required."

    @classmethod
    def make(cls, scons_args: Dict[str, str], is_debug: bool) -> ApioArgs:
        """Return a ApioArgs object with the parsed args."""
        parser = ApioArgsParser(scons_args, is_debug)

        # -- This is a flag we parsed eariler in the scons dispatcher but we
        # -- parse it here again so it doen's trigger the 'ignored arg'
        # -- error below.
        parser.arg_bool("debug")

        # -- Parse the args and populate an ApioArgs instance.
        result = ApioArgs(
            # Scons tring args.
            PROG=parser.arg_str("prog"),
            PLATFORM_ID=parser.arg_str("platform_id"),
            FPGA_ARCH=parser.arg_str("fpga_arch"),
            FPGA_PART_NUM=parser.arg_str("fpga_part_num"),
            FPGA_TYPE=parser.arg_str("fpga_type"),
            FPGA_PACK=parser.arg_str("fpga_pack"),
            TOP_MODULE=parser.arg_str("top_module"),
            TESTBENCH=parser.arg_str("testbench"),
            VERILATOR_NOWARNS=parser.env_str_list(
                "nowarn", ",", strip=True, keep_empty=False
            ),
            VERILATOR_WARNS=parser.env_str_list(
                "warn", ",", strip=True, keep_empty=False
            ),
            GRAPH_SPEC=parser.arg_str("graph_spec"),
            # Scons bool args
            VERBOSE_ALL=parser.arg_bool("verbose_all"),
            VERBOSE_YOSYS=parser.arg_bool("verbose_yosys"),
            VERBOSE_PNR=parser.arg_bool("verbose_pnr"),
            FORCE_SIM=parser.arg_bool("force_sim"),
            VERILATOR_ALL=parser.arg_bool("all"),
            VERILATOR_NO_STYLE=parser.arg_bool("nostyle"),
            # Env str vars.
            YOSYS_PATH=parser.env_var_str("YOSYS_LIB"),
            TRELLIS_PATH=parser.env_var_str("TRELLIS"),
        )

        # -- Check that all args were parsed.
        parser.check_all_args_parsed()

        return result
