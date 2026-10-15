"""A python script to generate COMMANDS.md."""

import sys
import json
import subprocess


def extract_command_list(node: dict, node_path: list[str]) -> list[list[str]]:
    """Recursively extract the commands from the json commands tree."""

    # -- Add the node to the list.
    result = [node_path]

    # -- Simple command, no children
    if "commands" not in node:
        return result

    for command, command_dict in node["commands"].items():
        command_path = node_path + [command]
        commands = extract_command_list(command_dict, command_path)
        result.extend(commands)

    # result = sorted(result)
    return result


def get_commands_list() -> list[list[str]]:
    """Run 'apio apio get-commands' and extract the commands list."""

    # -- Get the command hierarchy as a JSON doc.
    result = subprocess.run(
        ["apio", "api", "get-commands"],
        capture_output=True,
        text=True,
        check=True,
        encoding="utf-8",
    )

    text = result.stdout

    # -- Skip spam lines at the beginning, for example if
    # -- APIO_REMOTE_CONFIG_URL env var is defined.
    lines = text.splitlines(keepends=True)

    start = None
    for i, line in enumerate(lines):
        if line.startswith("{"):
            start = i
            break

    assert start is not None, "'{' line not found"

    json_text = "".join(lines[start:])

    data = json.loads(json_text)

    commands = extract_command_list(data["commands"]["apio"], ["apio"])

    return commands


def main():
    """Get the apio command list and dump their --help text."""
    commands = get_commands_list()

    commands = sorted(commands)

    for command in commands:
        command_str = " ".join(command)
        print(command_str, file=sys.stderr)

        result = subprocess.run(
            command + ["-h"],
            capture_output=True,
            text=True,
            check=True,
            encoding="utf-8",
        )

        print("\n--------------------------------------------\n")
        print(command_str)
        print()
        print(result.stdout)


if __name__ == "__main__":
    main()
