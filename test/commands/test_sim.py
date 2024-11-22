"""
  Test for the "apio sim" command
"""

# -- apio sim entry point
from apio.commands.sim import cli as cmd_sim


def test_sim(click_cmd_runner, setup_apio_test_env):
    """Test: apio sim
    when no apio.ini file is given
    No additional parameters are given
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- apio sim --board icezum
        result = click_cmd_runner.invoke(cmd_sim)
        assert result.exit_code != 0, result.output
        # -- TODO
