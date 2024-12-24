"""
  Test for the "apio" (root) command.
"""

from test.conftest import ApioRunner

# -- apio entry point
from apio.__main__ import cli as apio_


def test_apio_cmd(apio_runner: ApioRunner):
    """Test the apio root command."""

    with apio_runner.in_sandbox() as sb:

        # -- Run 'apio'
        result = sb.invoke_apio_cmd(apio_)
        sb.assert_ok(result)
        assert "Work with FPGAs with ease" in result.output
        assert "Build commands:" in result.output
        assert "Upload the bitstream to the FPGA" in result.output

        # -- Run 'apio --help'
        result = sb.invoke_apio_cmd(apio_, ["--help"])
        sb.assert_ok(result)
        assert "Work with FPGAs with ease" in result.output
        assert "Build commands:" in result.output
        assert "Upload the bitstream to the FPGA" in result.output

        # -- Run 'apio --version'
        result = sb.invoke_apio_cmd(apio_, ["--version"])
        sb.assert_ok(result)
        # -- Normally this should be 'apio, version ...' but in our test
        # -- environment we get 'cli'.
        assert "cli, version" in result.output

        # -- Run 'apio badcommand'
        result = sb.invoke_apio_cmd(apio_, ["badcommand"])
        assert result.exit_code != 0
        assert "Error: No such command 'badcommand'" in result.output
