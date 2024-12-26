"""
  Test for the "apio format" command
"""

from test.conftest import ApioRunner
from apio.commands.apio_format import cli as apio_format


def test_format_without_apio_ini(apio_runner: ApioRunner):
    """Tests the apio format command with a missing apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio format" with no apio.ini
        result = sb.invoke_apio_cmd(apio_format)
        assert result.exit_code != 0, result.output
        assert "Error: missing project file apio.ini" in result.output


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_format_with_apio_ini(apio_runner: ApioRunner):
    """Tests the apio format command with an apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio format" with a valid apio.ini.
        sb.write_default_apio_ini()
        result = sb.invoke_apio_cmd(apio_format)
        assert result.exit_code == 1, result.output
        assert "package 'verible' is not installed" in result.output
