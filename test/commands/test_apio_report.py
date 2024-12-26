"""
  Test for the "apio report" command
"""

from test.conftest import ApioRunner

# -- apio report entry point
from apio.commands.apio_report import cli as apio_report


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_report_no_apio(apio_runner: ApioRunner):
    """Tests the apio report command without an apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio report" without apio.ini
        result = sb.invoke_apio_cmd(apio_report)
        assert result.exit_code != 0, result.output
        assert "Error: missing project file apio.ini" in result.output


def test_report_with_apio(apio_runner: ApioRunner):
    """Tests the apio report command with an apio.ini file."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio report" with apio.ini
        sb.write_default_apio_ini()
        result = sb.invoke_apio_cmd(apio_report)
        assert result.exit_code != 0, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output
