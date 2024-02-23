"""
  Test for the "apio time" command
"""

# -- apio time entry point
from apio.commands.time import cli as cmd_time


def test_time(clirunner, configenv):
    """Test: apio time
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio time"
        result = clirunner.invoke(cmd_time)

        # -- Check the result
        assert result.exit_code != 0
        assert 'Info: No apio.ini file' in result.output
        assert 'Error: insufficient arguments: missing board' in result.output


def test_time_board(clirunner, configenv):
    """Test: apio time
    when parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio time"
        result = clirunner.invoke(cmd_time, ['--board', 'icezum'])

        # -- Check the result
        assert result.exit_code != 0
        assert 'apio install oss-cad-suite' in result.output
