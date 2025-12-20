"""Test for the "apio build" command."""

from pathlib import Path
from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_build_without_apio_ini(apio_runner: ApioRunner):
    """Tests build command with no apio.ini."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio build" without apio.ini
        result = sb.invoke_apio_cmd(apio, ["build"])
        assert result.exit_code != 0, result.output
        assert "Error: Missing project file apio.ini" in result.output


def test_build_with_apio_ini(apio_runner: ApioRunner):
    """Test build command with apio.ini."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio build" with a missing board var.
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, ["build"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Missing required option 'board' for env 'default'"
            in result.output
        )

        # -- Run "apio build" with an invalid board
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "no-such-board",
                    "top-module": "main",
                }
            }
        )
        result = sb.invoke_apio_cmd(apio, ["build"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Unknown board id 'no-such-board' in apio.ini"
            in result.output
        )

        # -- Run "apio build" with an unknown option.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                    "top-module": "main",
                    "unknown": "xyz",
                }
            }
        )
        result = sb.invoke_apio_cmd(apio, ["build"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Unknown option 'unknown' in [env:default] section "
            "of apio.ini" in result.output
        )


def test_build_with_env_arg_error(apio_runner: ApioRunner):
    """Tests the command with an invalid --env value. This error message
    confirms that the --env arg was propagated to the apio.ini loading
    logic."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio build --env no-such-env"
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, ["build", "--env", "no-such-env"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Env 'no-such-env' not found in apio.ini" in result.output
        )


def test_files_order(apio_runner: ApioRunner):
    """Tests that source files are sorted in apio build command."""

    with apio_runner.in_sandbox() as sb:

        # -- Fetch a working example.
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch", "alhambra-ii/ledon"],
            terminal_mode=False,
        )

        # -- Add dummy source files
        Path("aa").mkdir(parents=True)
        Path("bb").mkdir(parents=True)
        Path("aa/bb.v").touch()
        Path("aa/cc.v").touch()
        Path("bb/aa.v").touch()

        # -- Add a fake source files in _build directory. It should not be
        # -- picked up.
        Path("_build").mkdir()
        Path("_build/zzz.v").touch()

        # -- 'apio build'
        result = sb.invoke_apio_cmd(apio, ["build"])
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output

        # -- Check that the source file from the _build directory was not
        # -- picked up.
        assert "zzz.v" not in result.output

        # -- Check that the files in the build command are sorted.
        # -- We adjust for the "/" vs "\" difference between Windows and Linux.
        expected_order = ["ledon.v", "aa/bb.v", "aa/cc.v", "bb/aa.v"]
        expected_text = " ".join([str(Path(f)) for f in expected_order])
        assert expected_text in result.output
