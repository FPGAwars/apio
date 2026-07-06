"""Test for the "apio raw" command."""

import os
import sys
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

        # -- Run 'apio raw -- echo hello'.
        result = sb.invoke_apio_cmd(
            apio, ["raw", "--", "echo", "hello"], in_subprocess=True
        )
        sb.assert_result_ok(result, bad_words=[])
        assert "hello" in result.output

        # -- Run a command without the required '--'
        result = sb.invoke_apio_cmd(apio, ["raw", "echo"], in_subprocess=True)
        assert result.exit_code != 0, result.output
        assert "command separator '--' was not found" in result.output

        # -- Run a command with a token before the '--' separator.
        result = sb.invoke_apio_cmd(
            apio, ["raw", "echo", "--", "--help"], in_subprocess=True
        )
        assert result.exit_code != 0, result.output
        assert "Invalid arguments: ['echo']" in result.output

        # -- Run 'apio raw -v'
        result = sb.invoke_apio_cmd(apio, ["raw", "-v"], in_subprocess=True)
        sb.assert_result_ok(result)
        assert "Environment settings:" in result.output
        assert "YOSYS_LIB" in result.output


def test_raw_preserves_argv_and_cwd(apio_runner: ApioRunner):
    """Tests that 'apio raw' passes the wrapped command's arguments
    verbatim as an argv list (no re-splitting at spaces, no quote
    mangling) and runs it in the caller's current directory. This is
    a regression test for a Windows bug where the args were joined with
    POSIX quoting and re-tokenized by cmd.exe, breaking paths with
    spaces or backslashes."""

    with apio_runner.in_sandbox() as sb:

        # -- A probe command that reports its cwd and its argv, one
        # -- element per line. Note that the sandbox's current directory
        # -- ('apio proj') contains a space.
        probe = (
            "import os, sys; "
            "print('PROBE-CWD=<' + os.getcwd() + '>'); "
            "[print('PROBE-ARG-%d=<%s>' % (i, a)) "
            "for i, a in enumerate(sys.argv[1:])]"
        )

        result = sb.invoke_apio_cmd(
            apio,
            [
                "raw",
                "--",
                sys.executable,
                "-c",
                probe,
                "a b c.txt",
                r"_build\default\hardware.bit",
            ],
            in_subprocess=True,
        )
        sb.assert_result_ok(result, bad_words=[])

        # -- The wrapped command must inherit the caller's cwd.
        assert f"PROBE-CWD=<{os.getcwd()}>" in result.output

        # -- An arg with spaces must arrive as a single argv element.
        assert "PROBE-ARG-0=<a b c.txt>" in result.output

        # -- An arg with backslashes must arrive verbatim, without
        # -- added quotes.
        assert "PROBE-ARG-1=<_build\\default\\hardware.bit>" in result.output

        # -- There must be no extra args from re-splitting.
        assert "PROBE-ARG-2" not in result.output
