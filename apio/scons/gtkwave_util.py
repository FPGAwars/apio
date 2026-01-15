# GTKWave related utils.

"""GTKWave related utilities for the Apio Scons sub process."""

import re
import sys
from typing import Tuple
from pathlib import Path
from vcdvcd import VCDVCD
from apio.common.apio_console import cerror

GTKW_AUTO_FILE_MARKER = "THIS FILE WAS GENERATED AUTOMATICALLY BY APIO"


def _get_gtkw_file_header(testbench_path: Path) -> str:
    """Return a header string for the auto generated .gtkw file. 'testbench'
    is the relative path of the testbench file."""

    # -- Normalized path with '/', even on windows.
    tb_path_posix = Path(testbench_path).as_posix()

    lines = [
        f"# GTKWave display configuration for 'apio sim {tb_path_posix}'",
        f"# {GTKW_AUTO_FILE_MARKER}. DO NOT EDIT IT MANUALLY!",
        f"# To customize this file, run 'apio sim {tb_path_posix}'",
        "# and save the file from GTKWave.",
        "",
        "[*] GTKWave Analyzer v3.4.0 (w)1999-2022 BSI",
        "",
        "[*]",
    ]

    return "\n".join(lines) + "\n"


def _signal_sort_key(s: str) -> Tuple[int, str]:
    """Given a signal name, returns a key to use for signals sorting."""
    lcs = s.lower()

    # -- Priority 1: clock signals..
    if re.search(r"clk|clock", s):
        return (1, lcs)

    # -- Priority 2: reset signals.
    if re.search(r"reset|rst", s):
        return (2, lcs)

    # -- Priority 3: all the rest.
    return (3, lcs)


def create_gtkwave_file(
    testbench_path: str, vcd_path: str, gtkw_path: str
) -> None:
    """Generates a GTKWave configuration file from a VCD file.

    Args:
        testbench_path (str): Path to the simulated testbench.
        vcd_path (str): Path to the input VCD file.
        gtkw_path (str): Path to the output GTKWave configuration file.
    """

    # -- Pattern for top levels signals. E.g. 'testbench.CLK'.
    pattern = re.compile(r"^[^.]+[.][^.]+$")

    # -- Parse the vcd file and load the signals that match the pattern.
    # -- Do not load the actual signals values, just the metadata.
    vcd = VCDVCD(vcd_path, signal_res=[pattern], store_tvs=False)

    # -- Get a list with raw names of matching signals.
    raw_signals = list(vcd.references_to_ids.keys())

    # -- Strip range suffixes such as "[31:0]""
    range_pattern = re.compile(r"\[\d+:\d+\]$")
    signals = [range_pattern.sub("", sig) for sig in raw_signals]

    # -- Use basic heuristics to sort the files.
    signals.sort(key=_signal_sort_key)

    # -- Write the output file.
    with open(gtkw_path, "w", encoding="utf-8") as f:
        f.write(_get_gtkw_file_header(testbench_path))
        for signal in signals:
            f.write(signal + "\n")


def is_user_gtkw_file(gtkw_path: str) -> bool:
    """Test if the given .gtkw file exists and contains user's saved
    GTKWave display configuration."""

    # pylint: disable=broad-exception-caught

    assert gtkw_path.endswith(".gtkw")

    # -- If doesn't exist than now.
    if not Path(gtkw_path).exists():
        return False

    # -- File exists, test the content.
    try:
        # with gtkw_path.open("r", encoding="utf-8", errors="replace") as f:
        with open(gtkw_path, "r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if GTKW_AUTO_FILE_MARKER in line:
                    # -- File contains the apio auto marker. Not a user file.
                    return False
        # -- Marker not found. Must be a user file.
        return True

    except Exception as e:
        cerror(
            f"Failed to scan existing .gtkw file {gtkw_path}",
            f"{type(e).__name__}: {e}",
        )
        sys.exit(1)
