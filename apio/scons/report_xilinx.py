"""
This script is called by the `nextpnr-xilinx` tool for generating
a report, because it lacks the option `--report`
"""

import json
import os
from pathlib import Path


# Get the output file path from env. Apio set it up before invoking
# nextpnr-xilinx which invokes this script.
value = os.environ.get("APIO_XILINX_REPORT_FILE")
if not value:
    raise RuntimeError(
        "Environment variable APIO_XILINX_REPORT_FILE is not set. "
        "It is a workaround that Apio uses to pass to the nextpnr-xilinx "
        "--post-route script the path of the report output file "
        "'_build/(env)/hardware.pnr'."
    )

report_file = Path(value)

print(f"[report_xilinx.py: writing report to {report_file}]")


# -- Ignore pylint errores
# pylint: disable=self-assigning-variable
# pylint: disable=undefined-variable
# pylint: disable=invalid-name

# -- Ignore all hte pylance and Flake8 errors related to
# -- ctx (that is generated dynamically when calling nextpnr-xilinx)
ctx = ctx  # noqa: F821 # pyright: ignore[reportUndefinedVariable]

# -- Collect total FPGA resources
resources_total = {}

for bel in ctx.getBels():
    bel_type = ctx.getBelType(bel)
    resources_total[bel_type] = resources_total.get(bel_type, 0) + 1

# -- Actual resources used by the current design
resources_used = {}
# pyright: ignore[reportUndefinedVariable]
for cell_name, cell_info in ctx.cells:
    cell_type = str(cell_info.type)
    resources_used[cell_type] = resources_used.get(cell_type, 0) + 1

# -- Build the final blank report json file
report = {"critical_paths": [], "fmax": {}, "utilization": {}}

# --- Fill in the report json
for res, avail in resources_total.items():
    res_values = {"available": avail, "used": resources_used.get(res, 0)}
    report["utilization"][res] = res_values
    # print(f"* {res}: {amount} / {resources_total[res]}")


# -- Fill in the per-clock fmax. Older nextpnr-xilinx builds (openxc7
# -- package < 2026-07-17) don't expose the timing results; leave the
# -- table empty for them, as before.
if hasattr(ctx, "reportClockFmaxJson"):
    fmax = json.loads(ctx.reportClockFmaxJson())
    for clk_net, vals in fmax.items():
        # -- Yosys internal net names don't survive the report formatter's
        # -- name cleanup; alias them. '$iopadmap$<port>' is the net yosys
        # -- inserts for a clock input port -> show the port name itself.
        if clk_net.startswith("$iopadmap$"):
            name = clk_net.removeprefix("$iopadmap$")
        elif clk_net.startswith("$"):
            name = "(internal) " + clk_net.split("$")[-1]
        else:
            name = clk_net
        report["fmax"][name] = vals

# -- Generate the report file
with open(report_file, "w", encoding="utf8") as f:
    json.dump(report, f, indent=4)
