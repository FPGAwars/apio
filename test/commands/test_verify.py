"""
  Test for the "apio verify" command
"""

from test.conftest import ApioRunner

# -- apio verify entry point
from apio.commands.verify import cli as apio_verify


def test_verify(apio_runner: ApioRunner):
    """Test: apio verify
    when no apio.ini file is given
    No additional parameters are given
    """

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio verify"
        result = sb.invoke_apio_cmd(apio_verify, ["--board", "icezum"])

        # -- Check the result
        assert result.exit_code != 0, result.output
        assert "apio packages --install --force oss-cad-suite" in result.output
