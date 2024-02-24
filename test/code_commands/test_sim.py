"""
  Test for the "apio sim" command
"""

# -- apio sim entry point
from apio.commands.sim import cli as cmd_sim


def test_sim(clirunner, configenv):
    """Test: apio sim
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- apio sim --board icezum
        result = clirunner.invoke(cmd_sim)
        assert result.exit_code != 0
        # -- TODO
