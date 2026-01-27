import re
import sys
from typing import List, Tuple, Optional
import pathlib

# TODO: Associate this with ports  (* iopad_external_pin *)
# TODO: Move parameters to #() section.

# def parse_ports(lines: List[str]) -> List[str]:
#     """
#     Extract port declarations from module body lines.
#     Returns list of (direction, port_decl) e.g. ("input", "D") or ("output", "[3:0] Q")
#     Only collects input/output (skips parameter, wire, reg, etc.)
#     """
#     ports = []
#     port_re = re.compile(
#         r"^\s*(input|output)\s*(?:wire|)\s*"
#         r"(?:(?:\[.*?\])?\s*\w+(?:\s*,\s*\w+)*\s*;|\[.*?\]\s*\w+\s*;)",
#         re.IGNORECASE,
#     )

#     for line in lines:
#         line = line.strip()
#         if not line or line.startswith("//") or line.startswith("/*"):
#             continue
#         if line.startswith("endmodule"):
#             break
#         if line.startswith("parameter") or line.startswith("localparam"):
#             continue

#         match = port_re.match(line)
#         if match:
#             # direction = match.group(1).lower()
#             # Extract the declaration part after direction
#             name = line[len(match.group(1)) :].strip()
#             # Remove trailing semicolon and extra spaces
#             name = re.sub(r"\s*;\s*$", "", name).strip()
#             ports.append(name)

#     return ports

def parse_port(line: str) -> Optional[str]:
    """
    Extract port declarations from module body lines.
    Returns list of (direction, port_decl) e.g. ("input", "D") or ("output", "[3:0] Q")
    Only collects input/output (skips parameter, wire, reg, etc.)
    """

    sline = line.strip()

    if sline.startswith("input") or sline.startswith("output"):
        return line.replace(";", "")
    
    return None

    # # ports = []
    # port_re = re.compile(
    #     r"^\s*(input|output)\s*(?:wire|)\s*"
    #     r"(?:(?:\[.*?\])?\s*\w+(?:\s*,\s*\w+)*\s*;|\[.*?\]\s*\w+\s*;)",
    #     re.IGNORECASE,
    # )

    # # for line in lines:
    # line = line.strip()
    # if not line or line.startswith("//") or line.startswith("/*"):
    #     return None
    # if line.startswith("endmodule"):
    #     return None
    # if line.startswith("parameter") or line.startswith("localparam"):
    #     return None

    # match = port_re.match(line)
    # if not match:
    #     print(f"*** Non patch: {line}")
    #     return None
    
    # direction = match.group(1).lower()
    # # Extract the declaration part after direction
    # name = line[len(match.group(1)) :].strip()
    # # Remove trailing semicolon and extra spaces
    # name = re.sub(r"\s*;\s*$", "", name).strip()
    # ports.append(name)

    # return ports


# def build_port_list(ports: List[Tuple[str, str]]) -> str:
#     """Convert collected ports to comma-separated list for module header."""
#     if not ports:
#         return ""

#     items = []
#     for direction, decl in ports:
#         # Add direction back
#         items.append(f"{direction} {decl}")

#     return ", ".join(items)


def process_verilog_file(input_path: str, output_path: str) -> None:

    #print(f"*** CWD = {str(pathlib.Path.cwd())}")

    with open(input_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split into lines for easier processing
    lines = content.splitlines()
    output_lines = []
    i = 0

    module_re = re.compile(
        r"^\s*(?:module|macromodule)\s+(\w+)\s*\(\s*\.{3}\s*\)\s*;?\s*$",
        re.IGNORECASE,
    )

    while i < len(lines):
        line = lines[i]
        # print(line)

        # if line.startswith("module"):
        #     print("At module")

        match = module_re.match(line)

        if not match:
            output_lines.append(line)
            i += 1
            continue

        # Handle a module
        module_name = match.group(1)
        # Start collecting body until we find endmodule
        # body_start = i + 1
        body_lines = []
        ports = []
        j = i + 1
        while j < len(lines):
            body_line = lines[j].rstrip()
            port = parse_port(body_line)
            if port:
                ports.append(port)
            else:
                body_lines.append(body_line)
            # body_lines.append(body_line)
            j += 1
            if re.match(r"^\s*endmodule", body_line, re.IGNORECASE):
                break

        # Extract ports from body
        # port_names = parse_ports(body_lines)
        port_list_str = ",\n".join(ports)

        # Reconstruct module header
        # if port_list_str:
        if ports:
            port_list_str = ",\n".join(ports)
            new_header = f"module {module_name} (\n{port_list_str});"
        else:
            new_header = f"module {module_name} ();"

        # else:
        #     new_header = f"module {module_name} ();"

        output_lines.append(new_header)
        output_lines.extend(body_lines)

        # Skip original header and add body (without duplicating endmodule yet)
        i = j  # will increment below

    # Write result
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        f.write("\n")  # ensure trailing newline

    # print(f"Processed {len(output_lines)} lines.")
    print(f"Output written to: {output_path}")


# Usage
if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #    print("Usage: python fix_yosys_lib_ports.py <input_lib_file.v> <output_lib_file.v>")
    #    sys.exit(1)
    #
    # input_file = sys.argv[1]
    # output_file = sys.argv[2]
    process_verilog_file("new_cells_bb.v", "_fixed_new_cells_bb.v")
