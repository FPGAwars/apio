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

# print("Running 'apio api get-boards'")
result = subprocess.run(
    ["apio", "api", "get-boards"], capture_output=True, text=True
)
assert result.returncode == 0, (result.stdout, result.stderr)

# print("Parsing JSON doc")
data = json.loads(result.stdout)
# print(json.dumps(data, indent=2))

# print(all_boards)

# print("Splitting boards by architecture")
board_groups: Dict[str, List[str]] = {}
for board_id, board_info in data["boards"].items():
    # print()
    # print(f"{board_info=}")
    arch = board_info["fpga"]["arch"]
    if arch not in board_groups:
        board_groups[arch] = []
    board_groups[arch].append(board_id)

# print(board_groups)
today = date.today()
today = today.strftime("%B %-d, %Y")

with open("BOARDS.md", "w") as f:

    print("\n# Supported FPGA Boards", file=f)
    print("\n<br>\n", file=f)
    print(
        f"> Generated on {today}. For the complete list run `apio boards`.",
        file=f,
    )
    print(
        "\n> Custom board definitions can be added in the project directory.\n",
        file=f,
    )
    for arch, board_ids in board_groups.items():

        print("<br>\n", file=f)
        print(f"### {arch.upper()} boards", file=f)
        print("", file=f)
        print("| BOARD-ID | SIZE | DESCRIPTION | FPGA |", file=f)
        print("| :----- | :---- | :---- | :---- |", file=f)
        for board_id in board_ids:
            board_info = data["boards"][board_id]
            print(
                "| {} | {} | {} | {} |".format(
                    board_id,
                    board_info["fpga"]["size"],
                    board_info["description"],
                    board_info["fpga"]["part-num"],
                ),
                file=f,
            )
        print("", file=f)

    print("<br>\n", file=f)
