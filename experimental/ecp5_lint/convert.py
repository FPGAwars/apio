"""Convert Yosys blackbox librarry file to a format that is acceptable
by the Verilator linter."""

import re
import sys
from typing import List, Tuple, Optional
import pathlib
from dataclasses import dataclass

IN_FILE = "new_cells_bb.v"
OUT_FILE = "_fixed_new_cells_bb.v"


@dataclass(frozen=True)
class Param:
    """Represents a parsed parameter."""

    name: str
    value: str


@dataclass(frozen=True)
class Port:
    """Represents a parsed input of output port."""

    direction: str
    name: str
    annotations: List[str]


@dataclass(frozen=True)
class Module:
    """Represents a parsed module."""

    name: str
    params: List[Param]
    ports: List[Port]


def parse_module(module_lines: List[str]) -> Param:
    """Parse module lines. First line is 'module...' and last one is
    'endmodule'."""

    module_match = re.match(r"^module ([^ ]+) \(\.\.\.\);$", module_lines[0])
    module_name = module_match.group(1)
    # print(f"{module_name=}")

    params: List[Param] = []
    ports: List[Port] = []
    port_annotations = []
    for line in module_lines[1:-1]:
        l = line.strip()
        # print(l)

        # -- Parse an annotation ine.
        if l.startswith("(*"):
            # -- Dedupe. As of Jan 2026, some annotations are duplicate.
            if l not in port_annotations:
                port_annotations.append(l)
            continue

        # -- Parse a parameter line
        if l.startswith("parameter"):
            assert not port_annotations
            param_match = re.match(r"^parameter ([^ ]+) = (.+);$", l)
            param_name = param_match.group(1)
            param_value = param_match.group(2)
            param = Param(param_name, param_value)
            # print(param)
            params.append(param)
            continue

        # -- Parse a port line
        if l.startswith("input") or l.startswith("output"):
            port_match = re.match(r"^(input|output) ([^ ]+);$", l)
            port_direction = port_match.group(1)
            port_name = port_match.group(2)
            port = Port(port_direction, port_name, port_annotations)
            # print(port)
            ports.append(port)
            port_annotations = []
            continue

        # -- Here when unknown module line.
        raise ValueError(f"Unknown module line: []")

    module = Module(module_name, params, ports)
    # print(module)
    return module


def parsed_module_to_output_lines(module: Module) -> List[str]:
    """Convet a module declaration to output lines."""
    result = []
    result.append(f"module {module.name} #(")

    # -- Emit params
    for i, param in enumerate(module.params):
        suffix = "," if (i < len(module.params) - 1) else ""
        line = f"    parameter {param.name} = {param.value}{suffix}"
        result.append(line)

    result.append(") (")

    # -- Emit ports
    for i, port in enumerate(module.ports):
        # -- Emit optional annotation lines
        for annotation in port.annotations:
            result.append(f"    {annotation}")
        # -- Emit port line
        suffix = "," if (i < len(module.ports) - 1) else ""
        line = f"    {port.direction} {port.name}{suffix}"
        result.append(line)

    result.append(");")
    result.append("endmodule")
    return result


def main():
    """Program main."""

    # -- Read input file
    lines = []
    with open(IN_FILE, "r", encoding="utf-8") as f:
        for line in f.readlines():
            lines.append(line.rstrip())

    print(f"Read {len(lines)} lines from '{IN_FILE}'")

    # -- Generate output lines
    output_lines = []
    i = 0

    while i < len(lines):
        line: str = lines[i]

        # -- If line is not a module start copy it to output.
        if not line.startswith("module"):
            # -- Pass as is.
            output_lines.append(line)
            i += 1

            # -- Add a comment after the first line
            if len(output_lines) == 1:
                output_lines.append("//")
                output_lines.append("// Also converted automatically to Verilator lint friendly syntax")
                output_lines.append("// Per https://github.com/YosysHQ/yosys/issues/5637")

            continue


        # -- Here when at module start, collect the module lines
        # -- up to, and including the moduleend.
        module_lines = []
        module_lines.append(line)
        i += 1
        while True:
            line = lines[i]
            i += 1
            module_lines.append(line)
            if line.startswith("endmodule"):
                break

        module = parse_module(module_lines)
        module_output_lines = parsed_module_to_output_lines(module)
        output_lines.extend(module_output_lines)

    # -- Write output lines to output file
    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        f.write("\n")  # ensure trailing newline

    # -- All done ok.
    print(f"Wrote {len(output_lines)} lines to '{OUT_FILE}'")


# -- Starting point.
main()
