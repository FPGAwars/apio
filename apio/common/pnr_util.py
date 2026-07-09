# -*- coding: utf-8 -*-
# -- This file is part of the Apio project
# -- (C) 2016-2024 FPGAwars
# -- Authors
# --  * Jesús Arroyo (2016-2019)
# --  * Juan Gonzalez (obijuan) (2019-2024)
# -- License GPLv2
"""Shared utilities for parsing nextpnr (.pnr) build-report artifacts.

This module is intentionally free of apio-internal dependencies so that
it can be imported by both the main-process CLI commands (e.g.
'apio api get-build-report') and by scons subprocess tools
(e.g. '_maybe_print_pnr_clocks_report') without creating circular imports.
"""

from typing import Dict


def extract_clocks_from_pnr(pnr_data: Dict) -> Dict:
    """Extract clock timing metrics from a parsed nextpnr JSON report.

    Transforms the raw 'fmax' section produced by nextpnr into a stable
    dictionary map suitable for machine-readable output::

        {"<clock_name>": {"fmax": <achieved_mhz>}, ...}

    Returns an empty dict when no clock data is present in the report.
    This explicit empty-dict guarantee means callers never receive a
    missing key and do not need to guard against KeyError or None.

    Args:
        pnr_data: The parsed JSON object from a nextpnr .pnr report file.

    Returns:
        A dict mapping each clock name to its achieved fmax in MHz,
        or {} when the 'fmax' section is absent or empty.
    """
    raw_fmax: Dict = pnr_data.get("fmax", {})
    clocks: Dict = {}
    for clock_name, clock_data in raw_fmax.items():
        achieved = clock_data.get("achieved")
        if achieved is not None:
            clocks[clock_name] = {"fmax": achieved}
    return clocks
