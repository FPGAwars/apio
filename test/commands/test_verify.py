"""
  Test for the "apio verify" command
"""

# -- apio verify entry point
from apio.commands.verify import cli as apio_verify


def test_verify(click_cmd_runner, setup_apio_test_env):
    """Test: apio verify
    when no apio.ini file is given
    No additional parameters are given
    """

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        setup_apio_test_env()

        # -- Execute "apio verify"
        result = click_cmd_runner.invoke(apio_verify, ["--board", "icezum"])

        # -- Check the result
        assert result.exit_code != 0, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output
