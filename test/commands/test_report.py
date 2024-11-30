"""
  Test for the "apio report" command
"""

from test.conftest import ApioRunner

# -- apio report entry point
from apio.commands.report import cli as apio_report


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_report(apio_runner: ApioRunner):
    """Test: apio report
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio report"
        result = sb.invoke_apio_cmd(apio_report)

        # -- Check the result
        assert result.exit_code != 0, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output


def test_report_board(apio_runner: ApioRunner):
    """Test: apio report
    when parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio report"
        result = sb.invoke_apio_cmd(apio_report, ["--board", "icezum"])

        # -- Check the result
        assert result.exit_code != 0, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output
