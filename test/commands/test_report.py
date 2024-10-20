"""
  Test for the "apio report" command
"""

# -- apio report entry point
from apio.commands.report import cli as cmd_report


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_report(clirunner, configenv):
    """Test: apio report
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio report"
        result = clirunner.invoke(cmd_report)

        # -- Check the result
        assert result.exit_code != 0, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output


def test_report_board(clirunner, configenv):
    """Test: apio report
    when parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio report"
        result = clirunner.invoke(cmd_report, ["--board", "icezum"])

        # -- Check the result
        assert result.exit_code != 0, result.output
        assert "apio install oss-cad-suite" in result.output
