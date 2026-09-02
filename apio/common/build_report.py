# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2018 FPGAwars
# -- Author Jesús Arroyo
# -- License GPLv2
# -- Derived from:
# ---- Platformio project
# ---- (C) 2014-2016 Ivan Kravets <me@ikravets.com>
# ---- License Apache v2
"""Utilities related to the build report file hardware.pnr."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List
from apio.common.apio_console import fatal_error


@dataclass(frozen=True)
class ResourceReport:
    """Represents the info of a single FPGA resource."""

    name: str
    available: int
    used: int
    percentage: float


@dataclass(frozen=True)
class ClockReport:
    """Represents the info of a single clock signal."""

    name: str
    fmax_mhz: float


@dataclass(frozen=True)
class BuildReport:
    """Represents FPGA resources utilization and clocks speeds."""

    resources: List[ResourceReport]
    clocks: List[ClockReport]


def read_build_report(pnr_json_file_path: Path) -> BuildReport:
    """Read the given hardware.pnr file, parse it, and return
    a summary in the form of a BuildReport object. Fatal error on any
    error. The resources and the clocks in the result are sorted
    alphabetically by name, case insensitive"""

    # pylint: disable=too-many-locals
    # pylint: disable=broad-exception-caught

    # -- Sanity checks
    assert isinstance(pnr_json_file_path, Path), type(pnr_json_file_path)
    assert pnr_json_file_path.name == "hardware.pnr", pnr_json_file_path

    # -- Read the json text from the file
    try:
        json_text = pnr_json_file_path.read_text(encoding="utf-8")
    except Exception as e:
        fatal_error(
            f"Failed to read {str(pnr_json_file_path)}",
            cause=e,
            info="Did you build successfully this project env?",
        )

    # -- Parse the json text into a dict.
    try:
        json_dict = json.loads(json_text)
    except Exception as e:
        fatal_error(
            f"Failed parsing json file: {str(pnr_json_file_path)}", cause=e
        )

    # -- ECP5 (TRELLIS project) has a slightly different format of internal
    # -- net name. We detect it by the existence of "TRELLIS" in at least
    # -- one resource name.
    is_ecp5 = any("TRELLIS" in key for key in json_dict["utilization"])

    # -- Collect resources
    resources: List[ResourceReport] = []
    for resource_name, vals in json_dict["utilization"].items():
        available: int = vals["available"]
        used: int = vals["used"]
        percentage: float = 100 * used / available
        resources.append(
            ResourceReport(resource_name, available, used, percentage)
        )

    # -- Sort resources alphabetically, case insensitive.
    resources.sort(key=lambda r: r.name.lower())

    # -- Collect clocks
    clocks: List[ClockReport] = []
    for clk_net, vals in json_dict["fmax"].items():
        # -- Break the clk net name into parts
        name_parts = clk_net.split("$")

        # -- Extract the user net name part. The location depends on the
        # -- architecture.
        if is_ecp5:
            name = name_parts[2]
        else:
            name = name_parts[0]

        # -- Remove trailing '_'. Otherwise, on alhambra-ii/pll example, the
        # -- internal clock 'sys_clk' is reported as 'sys_clk_'.
        name = name.rstrip("_")

        # -- Extract max speed
        fmax_mhz = vals["achieved"]

        # -- Append to clock list.
        clocks.append(ClockReport(name, fmax_mhz))

    # -- Sort clocks alphabetically, case insensitive.
    clocks.sort(key=lambda r: r.name.lower())

    result = BuildReport(resources, clocks)
    return result
