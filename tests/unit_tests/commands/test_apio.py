# This file is part of the Apio project
# (C) 2016-present FPGAwars
# Project authors:
#   * Jesús Arroyo (Jesus89) (2016-2019)
#   * Juan Gonzalez (obijuan) (2019-2024)
#   * The Apio Team (2024-present)
# License: GPLv2

"""Test for the "apio" (root) command."""

from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_apio_cmd(apio_runner: ApioRunner):
    """Test the apio root command."""

    with apio_runner.in_sandbox() as sb:

        # -- Run 'apio'
        result = sb.invoke_apio_cmd(apio, [])
        sb.assert_result_ok(result)
        assert "WORK WITH FPGAs WITH EASE." in result.output
        assert "Build commands:" in result.output
        assert "Upload the bitstream to the FPGA" in result.output

        # -- Run 'apio --help'
        result = sb.invoke_apio_cmd(apio, ["--help"])
        sb.assert_result_ok(result)
        assert "WORK WITH FPGAs WITH EASE." in result.output
        assert "Build commands:" in result.output
        assert "Upload the bitstream to the FPGA" in result.output

        # -- Run 'apio --version'
        result = sb.invoke_apio_cmd(apio, ["--version"])
        sb.assert_result_ok(result)
        assert "Apio CLI " in result.output

        # -- Run 'apio badcommand'
        result = sb.invoke_apio_cmd(apio, ["badcommand"])
        assert result.exit_code != 0
        assert "Error: No such command 'badcommand'" in result.output
