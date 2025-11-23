"""Test for the "apio raw" command."""

from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_raw(apio_runner: ApioRunner):
    """Test "apio raw" with different parameters"""

    with apio_runner.in_sandbox() as sb:

        # -- NOTE: We run the apio raw command in a sub process to have a
        # -- proper sys.argv for it for the '--' separator validation.

        # -- Execute "apio raw"
        result = sb.invoke_apio_cmd(apio, ["raw"], in_subprocess=True)
        assert result.exit_code != 0, result.output
        assert (
            "at least one of --verbose or COMMAND must be specified"
            in result.output
        )

        # -- Execute "apio raw -v"
        result = sb.invoke_apio_cmd(apio, ["raw", "-v"], in_subprocess=True)
        sb.assert_result_ok(result)
        assert "Environment settings:" in result.output
        assert "PATH" in result.output
        assert "YOSYS_LIB" in result.output

        # -- Run 'apio raw  "nextpnr-ice40 --help"'.
        result = sb.invoke_apio_cmd(
            apio, ["raw", "--", "nextpnr-ice40", "--help"], in_subprocess=True
        )
        sb.assert_result_ok(result, bad_words=[])

        # -- Run a command without the required '--'
        result = sb.invoke_apio_cmd(
            apio, ["raw", "nextpnr-ice40"], in_subprocess=True
        )
        assert result.exit_code != 0, result.output
        assert "command separator '--' was not found" in result.output

        # -- Run a command with a token before the '--' separator.
        result = sb.invoke_apio_cmd(
            apio, ["raw", "nextpnr-ice40", "--", "--help"], in_subprocess=True
        )
        assert result.exit_code != 0, result.output
        assert "Invalid arguments: ['nextpnr-ice40']" in result.output

        # -- Run 'apio raw -v'
        result = sb.invoke_apio_cmd(apio, ["raw", "-v"], in_subprocess=True)
        sb.assert_result_ok(result)
        assert "Environment settings:" in result.output
        assert "YOSYS_LIB" in result.output
