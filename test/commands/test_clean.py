"""
  Test for the "apio clean" command
"""

# -- apio clean entry point
from apio.commands.clean import cli as cmd_clean

# -- apio create entry point
from apio.commands.create import cli as cmd_create


def test_clean(clirunner, configenv):
    """Test: apio clean
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio clean"
        result = clirunner.invoke(cmd_clean)

        # -- It is an error. Exit code should not be 0
        assert result.exit_code != 0, result.output
        assert "Info: Project has no apio.ini file" in result.output
        assert "Error: insufficient arguments: missing board" in result.output

        # -- Execute "apio clean --board alhambra-ii"
        result = clirunner.invoke(cmd_clean, ["--board", "alhambra-ii"])
        assert result.exit_code != 0, result.output


def test_clean_create(clirunner, configenv):
    """Test: apio clean
    when there is an apio.ini file
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # apio create --board icezum
        result = clirunner.invoke(cmd_create, ["--board", "alhambra-ii"])
        assert result.exit_code == 0, result.output
        assert "Creating apio.ini file ..." in result.output
        assert "was created successfully" in result.output

        # --- Execute "apio clean"
        result = clirunner.invoke(cmd_clean)
        assert result.exit_code != 0, result.output
