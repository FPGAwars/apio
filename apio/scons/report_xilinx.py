"""
This script is called by the `nextpnr-xilinx` tool for generating
a report, because it lacks the option `--report`
"""

import json
import os
from pathlib import Path


# -- DEBUG: show all the env variables
# variables = os.environ
# print(f"{'VARIABLE':<30} | {'VALUE'}")
# print("-" * 80)

# # Short it alfabetically
# for key in sorted(variables.keys()):
#     value = variables[key]
#     print(f"{key:<30} | {value}")

# import sys
# sys.exit()

# -- Read the ENV_BUILD_PATH variable, with the build environment folder
env_build_path = Path(os.environ["ENV_BUILD_PATH"])
# print(f"* env_build_path: {env_build_path}")

# -- Report file
report_file = env_build_path / "hardware.pnr"

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
for res, amount in resources_used.items():
    cell = {"available": resources_total[res], "used": amount}
    report["utilization"][res] = cell
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
            name = clk_net[len("$iopadmap$"):]
        elif clk_net.startswith("$"):
            name = "(internal) " + clk_net.split("$")[-1]
        else:
            name = clk_net
        report["fmax"][name] = vals

# -- Generate the report file
with open(report_file, "w", encoding="utf8") as f:
    json.dump(report, f, indent=4)
