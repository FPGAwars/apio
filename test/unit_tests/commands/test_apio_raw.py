"""Test for the "apio raw" command."""

from test.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_raw(apio_runner: ApioRunner):
    """Test "apio raw" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- Execute "apio raw"
        result = sb.invoke_apio_cmd(apio, ["raw"])
        assert result.exit_code != 0, result.output
        assert (
            "at least one of --verbose or COMMAND must be specified"
            in result.output
        )

        # -- Execute "apio raw -v"
        result = sb.invoke_apio_cmd(apio, ["raw", "-v"])
        sb.assert_ok(result)
        assert "Environment settings:" in result.output
        assert "PATH" in result.output
        assert "YOSYS_LIB" in result.output

        # -- Run 'apio raw  "nextpnr-ice40 --help"'
        result = sb.invoke_apio_cmd(
            apio, ["raw", "--", "nextpnr-ice40", "--help"]
        )
        sb.assert_ok(result)

        # -- Run 'apio raw -v'
        result = sb.invoke_apio_cmd(apio, ["raw", "-v"])
        sb.assert_ok(result)
        assert "Environment settings:" in result.output
        assert "YOSYS_LIB" in result.output
