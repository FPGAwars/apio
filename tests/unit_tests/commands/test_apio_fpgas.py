"""Test for the "apio boards" command."""

from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio

CUSTOM_FPGAS = """
{
  "custom-ice40hx4k-bg121": {
    "part-num": "CUSTOM-ICE40HX4K-BG121",
    "arch": "ice40",
    "size": "4k",
    "type": "hx4k",
    "pack": "bg121"
  },
  "ice40hx4k-tq144-8k": {
    "part-num": "MODIFIED-ICE40HX4K-TQ144",
    "arch": "ice40",
    "size": "8k",
    "type": "hx8k",
    "pack": "tq144:4k"
  }
}
"""


def test_fpgas_ok(apio_runner: ApioRunner):
    """Test "apio fpgas" command with standard fpgas.jsonc."""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio fpgas"
        result = sb.invoke_apio_cmd(apio, ["fpgas"])
        sb.assert_result_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio fpgas' | cat' to reproduce it.
        assert "Loading custom 'fpgas.jsonc'" not in result.output
        assert "ice40hx4k-tq144-8k" in result.output
        assert "my_custom_fpga" not in result.output
        assert "─────┐" in result.output  # Graphic table border
        assert ":---" not in result.output  # Graphic table border

        # -- Execute "apio fpgas --docs"
        result = sb.invoke_apio_cmd(apio, ["fpgas", "--docs"])
        sb.assert_result_ok(result)
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

        # -- Execute "apio fpgas". It should include the customization.
        result = sb.invoke_apio_cmd(apio, ["fpgas"])
        sb.assert_result_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio build' | cat' to reproduce it.
        assert "Loading custom 'fpgas.jsonc'" in result.output
        assert "gw1nz-lv1qn48c6-i5" in result.output
        assert "custom-ice40hx4k-bg121" in result.output
        assert "ice40hx4k-tq144-8k" in result.output
        assert "CUSTOM-ICE40HX4K-BG121" in result.output

        # -- Execute "apio fpgas --docs". It should not include the
        # -- customization.
        result = sb.invoke_apio_cmd(apio, ["fpgas", "--docs"])
        sb.assert_result_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        # -- Run 'apio build' | cat' to reproduce it.
        assert "Loading custom 'fpgas.jsonc'" not in result.output
        assert "gw1nz-lv1qn48c6-i5" in result.output
        assert "custom-ice40hx4k-bg121" not in result.output
        assert "ice40hx4k-tq144-8k" in result.output
        assert "CUSTOM-ICE40HX4K-BG121" not in result.output
