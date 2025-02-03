"""
  Test for the "apio" (root) command.
"""

from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_apio_cmd(apio_runner: ApioRunner):
    """Test the apio root command."""

    with apio_runner.in_sandbox() as sb:

        # -- Run 'apio'
        result = sb.invoke_apio_cmd(apio)
        sb.assert_ok(result)
        assert "WORK WITH FPGAs WITH EASE." in result.output
        assert "Build commands:" in result.output
        assert "Upload the bitstream to the FPGA" in result.output

        # -- Run 'apio --help'
        result = sb.invoke_apio_cmd(apio, "--help")
        sb.assert_ok(result)
        assert "WORK WITH FPGAs WITH EASE." in result.output
        assert "Build commands:" in result.output
        assert "Upload the bitstream to the FPGA" in result.output

        # -- Run 'apio --version'
        result = sb.invoke_apio_cmd(apio, "--version")
        sb.assert_ok(result)
        assert "apio, version" in result.output

        # -- Run 'apio badcommand'
        result = sb.invoke_apio_cmd(apio, "badcommand")
        assert result.exit_code != 0
        assert "Error: No such command 'badcommand'" in result.output
