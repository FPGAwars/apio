from typing import List, Set, Dict
from dataclasses import dataclass
import json
from pathlib import Path
from enum import Enum
import colorsys
import hashlib

# NOTE: To render the .dot online use
# https://www.tools-online.app/tools/graphviz


# YOSYS_JSON_FILE = "data/hardware-gowin1-256.json"
# NETS = {6, 144, 97, 135, 137, 71, 136, 138, 139}

# YOSYS_JSON_FILE = "data/hardware-gowin2-external.json"
# NETS = {6, 222}

YOSYS_JSON_FILE = "data/hardware-gowin2-internal.json"
NETS = {6, 140}


# -- Adjust for the design.
TOP_MODULE_NAME = "main"


class Direction(Enum):
    """Represents the direction(s) of a port."""

    IN = 1
    OUT = 2
    INOUT = 3

    def from_string(dir: str):
        """Given a direction string from the yosys .json file, return its
        matching Direction."""
        if dir in ["input"]:
            return Direction.IN
        if dir in ["output"]:
            return Direction.OUT
        if dir in ["inout", "IO"]:
            return Direction.INOUT
        raise ValueError(f"Unknown direction string: {dir}")


@dataclass(frozen=False)
class Port:
    """Represents a single port."""

    name: str
    direction: Direction
    net_nums: Set[int]

    def input_nets(self) -> Set[int]:
        """Returns the set of net numbers this port may use as an input."""
        if self.direction in [Direction.IN, Direction.INOUT]:
            return self.net_nums
        else:
            return set()

    def output_nets(self) -> Set[int]:
        """Returns the set of net numbers this port may use as an output."""
        if self.direction in [Direction.OUT, Direction.INOUT]:
            return self.net_nums
        else:
            return set()

    def all_nets(self) -> Set[int]:
        result = set()
        result.update(self.input_nets())
        result.update(self.output_nets())
        return result


@dataclass(frozen=False)
class Module:
    """Represents a single module or cell."""

    name: str
    parents: List[Module]
    ports: List[Port]
    children: List[Module]

    def input_nets(self) -> Set[int]:
        """Returns the set of net numbers this module may use as an input."""
        result = set()
        for port in self.ports:
            result.update(port.input_nets())
        for child in self.children:
            result.update(child.input_nets())
        return result

    def output_nets(self) -> Set[int]:
        """Returns the set of net numbers this module may use as an output."""
        result = set()
        for port in self.ports:
            result.update(port.output_nets())
        for child in self.children:
            result.update(child.output_nets())
        return result


@dataclass(frozen=False)
class Design:
    """Represents a single yosys design synthesis."""

    top_module: Module
    all_modules: List[Module]
    leaf_modules: List[Module]


def parse_module(
    module_name: str,
    module_json: dict,
    parents: List[Module],
) -> Module:
    """Parse a module tree and return the result as a top Module."""
    module = Module(
        name=module_name,
        parents=parents,
        ports=[],  # Filled below
        children=[],  # Filled below
    )
    if "cells" in module_json:
        for child_name, child_data in module_json["cells"].items():
            if not child_data["hide_name"]:
                child = parse_module(
                    child_name,
                    child_data,
                    parents + [module],
                )
                module.children.append(child)
                # children.append(child)
                # all_modules.extend(all)

    # ports: List[Port] = []
    if "ports" in module_json:
        for port_name, port_data in module_json["ports"].items():
            # direction = port_data["direction"]
            # print(port_name)
            # assert direction in ["input", "output", "IO", "inout"], direction
            direction = Direction.from_string(port_data["direction"])
            nets_nums = port_data["bits"]
            # print(module_name)
            # print(port_name)
            # print(nets)
            # assert len(nets) == 1
            port = Port(port_name, direction, set(nets_nums))
            module.ports.append(port)
            # ports.append(port)

    # See probe_data_out_OBUF_O as an example.
    elif "port_directions" in module_json:
        for port_name, direction_str in module_json["port_directions"].items():
            direction = Direction.from_string(direction_str)
            nets_nums = module_json["connections"][port_name]
            port = Port(port_name, direction, set(nets_nums))
            module.ports.append(port)
            # ports.append(port)

    return module


def parse_design(yosys_json: Dict) -> Design:

    # Extract the json dict of the top module.
    modules_json = yosys_json["modules"]
    top_model_json = modules_json[TOP_MODULE_NAME]

    # -- Parse the top module tree of modules.
    top_module = parse_module(
        module_name=TOP_MODULE_NAME,
        module_json=top_model_json,
        parents=[],
    )

    # print()

    # -- Collect a list of all modules in teh top module tree.
    all_modules = get_module_list(top_module)

    leaf_modules = [m for m in all_modules if not m.children]

    return Design(
        top_module=top_module,
        all_modules=all_modules,
        leaf_modules=leaf_modules,
    )


def dot_net_color(net_num: int) -> str:
    """
    Deterministic pseudo-random color for a given net number.
    Returns a Graphviz-compatible hex color (#RRGGBB).
    """
    # Create a consistent hash from the net number
    h = hashlib.sha256(str(net_num).encode()).hexdigest()

    # Take first 8 hex chars → integer 0..0xFFFFFFFF
    hue_value = int(h[:8], 16)

    # Map to hue in [0.0, 1.0] — full color wheel
    hue = (hue_value / 0xFFFFFFFF) % 1.0

    # Fixed saturation & value → vivid but not blinding colors
    saturation = 0.90
    value = 0.92

    # Convert HSV → RGB → hex
    r, g, b = colorsys.hsv_to_rgb(hue, saturation, value)
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"


def gen_dot_graph(design: Design, nets: Set[int]):
    with open("_graph.dot", "w", encoding="utf-8") as f:

        f.write("digraph D {\n")
        f.write('node [fontname="Arial"];\n\n')

        # -- Write net nodes
        for net in nets:
            f.write(
                f'net_{net} [label="net {net}", shape=plaintext, fontsize=10];\n'
            )

        modules = []
        for module in design.leaf_modules:
            if not nets.isdisjoint(module.output_nets()):
                modules.append(module)

        for module in modules:
            # TODO: pass prefix ignore list.
            if module.name != "async_fifo.mem.0":
                nets.update(module.input_nets())

        # -- Write module nodes.
        for module in modules:
            inputs = []
            outputs = []
            for port in module.ports:
                tag = f"<{port.name}> {port.name}"
                if port.output_nets():
                    outputs.append(tag)
                else:
                    inputs.append(tag)

            f.write(
                '"'
                + module.name
                + '" [shape=record, label = "{'
                + "|".join(inputs)
                + "} | "
                + module.name
                + " | {"
                + "|".join(outputs)
                + '}"];\n'
            )

        # -- Write net edges
        f.write("\n")
        for net in nets:
            net_color = dot_net_color(net)
            for module in modules:
                for port in module.ports:
                    if net in port.input_nets():
                        if module.name != "async_fifo.mem.0.0":
                            f.write(
                                f'net_{net} -> "{module.name}":"{port.name}" '
                                f'[label="", arrowhead=normal, style=solid, penwidth=1.5, color="{net_color}"];\n'
                            )
                    if net in port.output_nets():
                        f.write(
                            f'"{module.name}":"{port.name}" -> net_{net} '
                            f'[arrowhead=none, style=solid, penwidth=1.5, color="{net_color}"];\n'
                        )

        f.write("}\n")


def get_module_list(root: Module) -> List[Module]:
    """Return a list of all modules in a tree."""
    result = [root]
    # Iterate recursively.
    for child in root.children:
        result.extend(get_module_list(child))
    return result


def main():

    # Read the yosys json file.
    with Path(YOSYS_JSON_FILE).open(encoding="utf-8") as f:
        yosys_json = json.load(f)

    # Parse into a Design object.
    design = parse_design(yosys_json)




    gen_dot_graph(design, NETS)


if __name__ == "__main__":
    main()
