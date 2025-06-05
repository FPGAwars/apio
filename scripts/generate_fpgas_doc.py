"""A python script to generate BOARDS.md"""

import os
import json
from typing import List, Self
from dataclasses import dataclass
from typing import Dict, List
import click
from click import secho
from datetime import date
from apio.commands.apio import cli as root
import subprocess

print("Running 'apio api get-fpgas'")
result = subprocess.run(
    ["apio", "api", "get-fpgas"], capture_output=True, text=True
)
assert result.returncode == 0, (result.stdout, result.stderr)

print("Parsing JSON doc")
data = json.loads(result.stdout)
# print(json.dumps(data, indent=2))

print("Splitting fpgas by architecture")
fpga_groups: Dict[str, List[str]] = {}
for fpga_id, fpga_info in data["fpgas"].items():
    # print()
    # print(f"{board_info=}")
    arch = fpga_info["arch"]
    if arch not in fpga_groups:
        fpga_groups[arch] = []
    fpga_groups[arch].append(fpga_id)

# print(board_groups)
today = date.today()
today = today.strftime("%B %-d, %Y")

with open("FPGAS.md", "w") as f:

    print("\n# Supported FPGAs", file=f)
    print("\n<br>\n", file=f)
    print(
        f"> Generated on {today}. For the complete list run `apio fpgas`.",
        file=f,
    )
    print(
        "\n> Custom fpga definitions can be added in the project directory.\n",
        file=f,
    )
    for arch, fpga_ids in fpga_groups.items():

        print("<br>\n", file=f)
        print(f"### {arch.upper()} FPGAs", file=f)
        print("", file=f)
        print("| FPGA-ID | SIZE | PART-NUM |", file=f)
        print("| :----- | :---- | :---- |", file=f)
        for fpga_id in fpga_ids:
            fpga_info = data["fpgas"][fpga_id]
            print(
                "| {} | {} | {} |".format(
                    fpga_id,
                    fpga_info["size"],
                    fpga_info["part-num"],
                ),
                file=f,
            )
        print("", file=f)

    print("<br>\n", file=f)

print("Updated FPGAS.md")
