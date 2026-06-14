import json

# --------------------------------------------------------------------------
# -- This script is called by the `nextpnr-xilinx` tool for generating
# -- a report, because it lacks the option `--report`
# --------------------------------------------------------------------------

# -- Report file
# -- TODO: It is wired now, but it should be read from the environmnet
REPORT_FILE = "_build/default/hardware.pnr"

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
report = {
    "critical_paths": [],
    "fmax": {},
    "utilization": {
    }
}

# --- Fill in the report json
for res, amount in resources_used.items():
    cell = {
        "available": resources_total[res],
        "used": amount
    }
    report["utilization"][res] = cell
    # print(f"* {res}: {amount} / {resources_total[res]}")

# -- Generate the report file
with open(REPORT_FILE, "w") as f:
    json.dump(report, f, indent=4)


# -- DEBUG: Mostrar las variables de entorno
# import os


# variables = os.environ
# print(f"{'VARIABLE':<30} | {'VALOR'}")
# print("-" * 80)

# # Ordenamos las claves alfabéticamente para que sea fácil localizarlas
# for clave in sorted(variables.keys()):
#     valor = variables[clave]
#     print(f"{clave:<30} | {valor}")
