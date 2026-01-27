import re
import sys
from typing import List, Tuple


def parse_ports(lines: List[str]) -> List[Tuple[str, str]]:
    """
    Extract port declarations from module body lines.
    Returns list of (direction, port_decl) e.g. ("input", "D") or ("output", "[3:0] Q")
    Only collects input/output (skips parameter, wire, reg, etc.)
    """
    ports = []
    port_re = re.compile(
        r"^\s*(input|output)\s*(?:wire|)\s*"
        r"(?:(?:\[.*?\])?\s*\w+(?:\s*,\s*\w+)*\s*;|\[.*?\]\s*\w+\s*;)",
        re.IGNORECASE,
    )

    for line in lines:
        line = line.strip()
        if not line or line.startswith("//") or line.startswith("/*"):
            continue
        if line.startswith("endmodule") or line.startswith("endprim"):
            break
        if line.startswith("parameter") or line.startswith("localparam"):
            continue

        match = port_re.match(line)
        if match:
            direction = match.group(1).lower()
            # Extract the declaration part after direction
            decl_part = line[len(match.group(1)) :].strip()
            # Remove trailing semicolon and extra spaces
            decl_part = re.sub(r"\s*;\s*$", "", decl_part).strip()
            ports.append((direction, decl_part))

    return ports


def build_port_list(ports: List[Tuple[str, str]]) -> str:
    """Convert collected ports to comma-separated list for module header."""
    if not ports:
        return ""

    items = []
    for direction, decl in ports:
        # Add direction back
        items.append(f"{direction} {decl}")

    return ", ".join(items)


def process_verilog_file(input_path: str, output_path: str) -> None:
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
        print(line)

        if line.startswith("module"):
            pass
            #print("At module")

        match = module_re.match(line)

        if match:
            module_name = match.group(1)
            # Start collecting body until we find endmodule
            body_start = i + 1
            body_lines = []
            j = body_start
            while j < len(lines):
                body_line = lines[j].rstrip()
                body_lines.append(body_line)
                if re.match(r"^\s*endmodule", body_line, re.IGNORECASE):
                    break
                j += 1

            # Extract ports from body
            ports = parse_ports(body_lines)
            port_list_str = build_port_list(ports)

            # Reconstruct module header
            if port_list_str:
                new_header = f"module {module_name} ({port_list_str});"
            else:
                new_header = f"module {module_name} ();"

            output_lines.append(new_header)

            # Skip original header and add body (without duplicating endmodule yet)
            i = j  # will increment below
        else:
            output_lines.append(line)

        i += 1

    # Write result
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(output_lines))
        f.write("\n")  # ensure trailing newline

    print(f"Processed {len(output_lines)} lines.")
    print(f"Output written to: {output_path}")


# Usage
if __name__ == "__main__":
    # if len(sys.argv) != 3:
    #    print("Usage: python fix_yosys_lib_ports.py <input_lib_file.v> <output_lib_file.v>")
    #    sys.exit(1)
    #
    # input_file = sys.argv[1]
    # output_file = sys.argv[2]
    process_verilog_file("original_cells_bb.v", "_modified_cells_bb.v")
