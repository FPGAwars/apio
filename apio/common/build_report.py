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
from typing import Any
from dataclasses import dataclass
from pathlib import Path
from apio.common.apio_console import fatal_error
from apio.common.proto.apio_common_pb2 import ApioArch


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

    arch: ApioArch
    resources: list[ResourceReport]
    clocks: list[ClockReport]


def _identify_build_architecture(json_dict: dict[str, Any]) -> ApioArch:
    """Given the content of the nextpnr json output file hardware.pnr,
    identify the architecture of the build."""

    # -- A set of patterns and their matching architectures.
    patterns = {
        "ICESTORM": ApioArch.ice40,
        "TRELLIS": ApioArch.ecp5,
        "IOLOGICI": ApioArch.gowin,
        "SLICE": ApioArch.xilinx,
    }

    # -- Collect all archs whose patterns match.
    matches: list[ApioArch] = []
    for pattern, arch in patterns.items():
        for key in json_dict["utilization"]:
            if pattern in key:
                matches.append(arch)
                break

    # -- Error if we got none or more than 1.
    if len(matches) != 1:
        fatal_error(f"Expected exactly 1 arch match, found: {matches}")

    # -- Found it.
    return matches[0]


def _parse_clk_net_name(clk_net: str, arch: ApioArch) -> str:
    """Given a clock net as it appears in the nextpnr file hardware.pnr,
    extracts and returns a user friendly clock name. The parsing of the
    clock net depends ont the fpga architecture of the build."""

    # -- Break the clk net name into parts
    name_parts = clk_net.split("$")

    # -- Handle ICE40
    if arch == ApioArch.ice40:
        return name_parts[0].rstrip("_")

    # -- Handle ECP5
    if arch == ApioArch.ecp5:
        return name_parts[2]

    # -- Handle Gowin
    if arch == ApioArch.gowin:
        return name_parts[0].removesuffix("_IBUF_I_O")

    # -- Handle Xilinx
    if arch == ApioArch.xilinx:
        return next(
            (part for part in reversed(name_parts) if part),
            "",
        )

    # -- Handle unknown architecture.
    fatal_error(f"Unexpected FPGA architecture: {arch}")


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

    # -- Identify the FPGA arch of the build.
    arch = _identify_build_architecture(json_dict)

    # -- Collect resources
    resources: list[ResourceReport] = []
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
    clocks: list[ClockReport] = []
    for clk_net, vals in json_dict["fmax"].items():
        # -- Extract a user friendly clock name.
        name = _parse_clk_net_name(clk_net, arch)

        # -- Extract max speed
        fmax_mhz = vals["achieved"]

        # -- Append to clock list.
        clocks.append(ClockReport(name, fmax_mhz))

    # -- Sort clocks alphabetically, case insensitive.
    clocks.sort(key=lambda r: r.name.lower())

    result = BuildReport(arch, resources, clocks)
    return result
