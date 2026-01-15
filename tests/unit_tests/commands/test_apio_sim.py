"""Test for the "apio sim" command"""

from pathlib import Path
from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_sim(apio_runner: ApioRunner):
    """Test apio sim without apio.ini. Should fail."""

    with apio_runner.in_sandbox() as sb:

        # -- apio sim
        result = sb.invoke_apio_cmd(apio, ["sim"])
        assert result.exit_code != 0, result.output
        assert "Missing project file apio.ini" in result.output


def test_sim_with_env_arg_error(apio_runner: ApioRunner):
    """Tests the command with an invalid --env value. This error message
    confirms that the --env arg was propagated to the apio.ini loading
    logic."""

    with apio_runner.in_sandbox() as sb:

        # -- Run "apio sim --env no-such-env"
        sb.write_apio_ini({"[env:default]": {"top-module": "main"}})
        result = sb.invoke_apio_cmd(apio, ["sim", "--env", "no-such-env"])
        assert result.exit_code == 1, result.output
        assert (
            "Error: Env 'no-such-env' not found in apio.ini" in result.output
        )


def test_sim_with_no_user_gtkw_file(apio_runner: ApioRunner):
    """Verify that 'apio sim' creates a default .gtkw file."""

    with apio_runner.in_sandbox() as sb:

        # -- Get example project.
        result = sb.invoke_apio_cmd(
            apio, ["examples", "fetch", "alhambra-ii/ledon"]
        )
        sb.assert_result_ok(result)

        # -- Verify it has a testbench gtkw file.
        gtkw_path = Path("ledon_tb.gtkw")
        assert gtkw_path.exists(), gtkw_path

        # -- Delete teh gtkw file.
        gtkw_path.unlink()
        assert not gtkw_path.exists(), gtkw_path

        # -- Run headless sim, it should create the gtkw file.
        result = sb.invoke_apio_cmd(apio, ["sim", "--no-gtkwave"])
        sb.assert_result_ok(result)
        assert gtkw_path.exists(), gtkw_path

        # -- Verify the file.
        content1 = gtkw_path.read_text(encoding="utf-8")
        timestamp1 = gtkw_path.stat().st_mtime
        assert "THIS FILE WAS GENERATED AUTOMATICALLY BY APIO" in content1
        assert "ledon_tb.DURATION" in content1
        assert "ledon_tb.led0" in content1

        # -- Run headless sim again, it should overwrite the gtkw file.
        result = sb.invoke_apio_cmd(apio, ["sim", "--no-gtkwave"])
        sb.assert_result_ok(result)
        assert gtkw_path.exists(), gtkw_path

        # -- Verify the file.
        content2 = gtkw_path.read_text(encoding="utf-8")
        timestamp2 = gtkw_path.stat().st_mtime
        assert content1 == content2
        assert timestamp1 != timestamp2


def test_sim_with_user_gtkw_file(apio_runner: ApioRunner):
    """Verify that 'apio sim' doesn't overwrite user saved .gtkw file."""

    with apio_runner.in_sandbox() as sb:

        # -- Get example project.
        result = sb.invoke_apio_cmd(
            apio, ["examples", "fetch", "alhambra-ii/ledon"]
        )
        sb.assert_result_ok(result)

        # -- Verify it has a testbench gtkw file.
        gtkw_path = Path("ledon_tb.gtkw")
        assert gtkw_path.exists(), gtkw_path

        # -- Verify the file.
        content1 = gtkw_path.read_text(encoding="utf-8")
        timestamp1 = gtkw_path.stat().st_mtime
        assert "THIS FILE WAS GENERATED AUTOMATICALLY BY APIO" not in content1

        # -- Run headless sim, it should create the gtkw file.
        result = sb.invoke_apio_cmd(apio, ["sim", "--no-gtkwave"])
        sb.assert_result_ok(result)
        assert gtkw_path.exists(), gtkw_path

        # -- Verify that the file was not changed file.
        content2 = gtkw_path.read_text(encoding="utf-8")
        timestamp2 = gtkw_path.stat().st_mtime
        assert content1 == content2
        assert timestamp1 == timestamp2
