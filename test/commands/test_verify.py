"""
  Test for the "apio verify" command
"""

# -- apio verify entry point
from apio.commands.verify import cli as cmd_verify


def test_verify(clirunner, configenv):
    """Test: apio verify
    when no apio.ini file is given
    No additional parameters are given
    """

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio verify"
        result = clirunner.invoke(cmd_verify, ['--board', 'icezum'])

        # -- Check the result
        assert result.exit_code != 0
        assert 'apio install oss-cad-suite' in result.output
