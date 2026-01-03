"""
Apio MCP Server - Proof of Concept

Exposes Apio testbench conventions as:
- A static resource with all rules
- A prompt template for testbench generation
- A tool returning the EXPECT_EQ macro

Install: pip install mcp
Run: python apio_mcp_server.py
"""

from mcp.server.fastmcp import FastMCP

# Initialize the MCP server (name only)
mcp = FastMCP("Apio Testbench Rules")

# Full rules as a single resource
APIO_TESTBENCH_RULES = """
Apio Testbench Conventions:

Rule 1: Define at the top of the file an assertion macro called EXPECT_EQ that compares an actual and expected value.
If the values do not match, print an error message with the expected and actual values as well as the file name and line number,
and exit using $fatal.

Rule 2: Use a boolean signal called assertion_err initialized to 0 and set it to 1 when an assertion fails.

Rule 3: Any time you use $fatal, qualify it with if (!`APIO_SIM) $fatal.

Rule 4: At the end of the testbench, print the message "End of simulation".

Rule 5: Use $dumpvars() with the testbench module name as an argument.

Rule 6: Do not use $dumpfile().
"""

@mcp.resource("apio://testbench-rules")
def get_testbench_rules() -> str:
    """Returns the complete set of Apio testbench rules."""
    return APIO_TESTBENCH_RULES.strip()

# Prompt template for testbench generation
TESTBENCH_PROMPT_TEMPLATE = """
You are an expert Verilog designer following Apio conventions.

Generate a complete testbench module for the provided DUT module.

Strictly adhere to these rules:
{testbench_rules}

The DUT module is:
{dut_code}

Output only the Verilog code for the testbench, no explanations.
"""

@mcp.prompt("apio://generate-testbench-prompt")
def generate_testbench_prompt(dut_code: str) -> str:
    """Prompt template for generating Apio-compliant testbenches."""
    return TESTBENCH_PROMPT_TEMPLATE.format(
        testbench_rules=APIO_TESTBENCH_RULES.strip(),
        dut_code=dut_code
    )

# Example tool returning the EXPECT_EQ macro
@mcp.tool()
def get_expect_eq_macro() -> str:
    """Returns the recommended EXPECT_EQ macro definition."""
    return """
`define EXPECT_EQ(actual, expected) \\
    if ((actual) !== (expected)) begin \\
        $display("ERROR: EXPECT_EQ failed - expected '%0d' but got '%0d' at %s:%0d", \\
                 (expected), (actual), `__FILE__, `__LINE__); \\
        assertion_err = 1; \\
        if (!`APIO_SIM) $fatal; \\
    end
"""

if __name__ == "__main__":
    print("Starting Apio MCP Server on http://localhost:8000/mcp")
    print("Connect from your VS Code AI client (e.g., Claude Code, Copilot Chat)")
    mcp.run(transport="streamable-http")