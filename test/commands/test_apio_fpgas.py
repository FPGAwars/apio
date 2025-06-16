"""Test for the "apio boards" command."""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio

CUSTOM_FPGAS = """
{
  "my_custom_fpga": {
    "arch": "ice40",
    "type": "lp1k",
    "size": "1k",
    "pack": "swg16tr"
  }
}
"""


def test_fpgas_ok(apio_runner: ApioRunner):
    """Test "apio fpgas" command with standard fpgas.jsonc."""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio fpgas"
        result = sb.invoke_apio_cmd(apio, ["fpgas"])
        sb.assert_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio fpgas' | cat' to reproduce it.
        assert "Loading custom 'fpgas.jsonc'" not in result.output
        assert "ice40hx4k-tq144-8k" in result.output
        assert "my_custom_fpga" not in result.output
        assert "─────┐" in result.output  # Graphic table border
        assert ":---" not in result.output  # Graphic table border

        # -- Execute "apio fpgas --docs"
        result = sb.invoke_apio_cmd(apio, ["fpgas", "--docs"])
        sb.assert_ok(result)
        assert "Loading custom 'fpgas.jsonc'" not in result.output
        assert "ice40hx4k-tq144-8k" in result.output
        assert "my_custom_fpga" not in result.output
        assert "─────┐" not in result.output  # Graphic table border
        assert ":---" in result.output  # Graphic table border


def test_custom_fpga(apio_runner: ApioRunner):
    """Test "apio fpgas" command with a custom fpgas.jsonc."""

    with apio_runner.in_sandbox() as sb:

        # -- Write apio.ini for apio to pick the project's default
        # -- fpgas.jsonc.
        sb.write_default_apio_ini()

        # -- Write a custom boards.jsonc file in the project's directory.
        sb.write_file("fpgas.jsonc", CUSTOM_FPGAS)

        # -- Execute "apio boards"
        result = sb.invoke_apio_cmd(apio, ["fpgas"])
        sb.assert_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio build' | cat' to reproduce it.
        assert "Loading custom 'fpgas.jsonc'" in result.output
        assert "ice40hx4k-tq144-8k" not in result.output
        assert "my_custom_fpga" in result.output
        assert "Total of 1 fpga" in result.output

        # -- Execute "apio fpgas --docs"
        # -- When running with --docs, 'apio boards' ignores custom fpgas.
        result = sb.invoke_apio_cmd(apio, ["fpgas", "--docs"])
        sb.assert_ok(result)
        assert "Loading custom 'fpgas.jsonc'" not in result.output
        assert "ice40hx4k-tq144-8k" in result.output
        assert "my_custom_fpga" not in result.output
        assert "─────┐" not in result.output  # Graphic table border
        assert ":---" in result.output  # Graphic table border
