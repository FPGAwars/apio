"""Test for the "apio clean" command."""

from os.path import join
from pathlib import Path
from test.conftest import ApioRunner
from apio.commands.apio import cli as apio


def test_clean_env_single(apio_runner: ApioRunner):
    """Tests the 'apio clean' command with a single env in _build. It should
    delete also the _build dir which is left empty after the cleanup.
    """

    with apio_runner.in_sandbox() as sb:

        sb.write_default_apio_ini()
        sb.write_file(".sconsign.dblite", "dummy text")
        sb.write_file("zadig.ini", "dummy text")
        sb.write_file("_build/default/hardware.out", "dummy text")

        assert Path(".sconsign.dblite").exists()
        assert Path("zadig.ini").exists()
        assert Path("_build/default/hardware.out").exists()

        result = sb.invoke_apio_cmd(apio, "clean")
        assert result.exit_code == 0, result.output

        assert "Removed .sconsign.dblite" in result.output
        assert "Removed zadig.ini" in result.output
        assert f"Removed {join('_build', 'default')}" in result.output
        assert "Removed _build" in result.output

        assert not Path(".sconsign.dblite").exists()
        assert not Path("zadig.ini").exists()
        assert not Path("_build/default").exists()
        assert not Path("_build").exists()


def test_clean_env_multiple(apio_runner: ApioRunner):
    """Tests the 'apio clean --env env2' with an additional _build/env1 env.
    It should leave _build/env1 intact.
    """

    with apio_runner.in_sandbox() as sb:

        sb.write_apio_ini(
            {
                "[env:env1]": {
                    "board": "alhambra-ii",
                    "top-module": "main",
                },
                "[env:env2]": {
                    "board": "alhambra-ii",
                    "top-module": "main",
                },
            }
        )

        sb.write_file(".sconsign.dblite", "dummy text")
        sb.write_file("_build/env1/hardware.out", "dummy text")
        sb.write_file("_build/env2/hardware.out", "dummy text")

        assert Path(".sconsign.dblite").exists()
        assert Path("_build/env1/hardware.out").exists()
        assert Path("_build/env2/hardware.out").exists()

        result = sb.invoke_apio_cmd(apio, "clean", "--env", "env2")
        assert result.exit_code == 0, result.output

        assert "Removed .sconsign.dblite" in result.output
        assert f"Removed {join('_build', 'env2')}" in result.output

        assert not Path(".sconsign.dblite").exists()
        assert not Path("_build/env2").exists()

        # -- The other env was not cleaned up.
        assert Path("_build/env1/hardware.out").exists()


def test_clean_env_all(apio_runner: ApioRunner):
    """Tests the 'apio clean --all' with two envs. It should delete _build."""

    with apio_runner.in_sandbox() as sb:

        sb.write_apio_ini(
            {
                "[env:env1]": {
                    "board": "alhambra-ii",
                    "top-module": "main",
                },
                "[env:env2]": {
                    "board": "alhambra-ii",
                    "top-module": "main",
                },
            }
        )

        sb.write_file(".sconsign.dblite", "dummy text")
        sb.write_file("_build/env1/hardware.out", "dummy text")
        sb.write_file("_build/env2/hardware.out", "dummy text")

        assert Path(".sconsign.dblite").exists()
        assert Path("_build/env1/hardware.out").exists()
        assert Path("_build/env2/hardware.out").exists()

        result = sb.invoke_apio_cmd(apio, "clean", "--env", "env2")
        assert result.exit_code == 0, result.output

        assert "Removed .sconsign.dblite" in result.output
        assert f"Removed {join('_build', 'env2')}" in result.output

        assert not Path(".sconsign.dblite").exists()
        assert not Path("_build/env2").exists()

        # -- The other env was not cleaned up.
        assert Path("_build/env1/hardware.out").exists()


def test_clean_env_no_build(apio_runner: ApioRunner):
    """Tests the 'apio clean' command with nothing to delete."""

    with apio_runner.in_sandbox() as sb:

        sb.write_default_apio_ini()

        assert not Path(".sconsign.dblite").exists()
        assert not Path("_build").exists()

        result = sb.invoke_apio_cmd(apio, "clean")
        assert result.exit_code == 0, result.output

        assert "Removed" not in result.output
        assert "Already cleaned up" in result.output


def test_clean_legacy_files(apio_runner: ApioRunner):
    """Tests that 'apio clean' deletes also legacy files that may have been
    left in the project dir.
    """

    with apio_runner.in_sandbox() as sb:

        legacy_files = [
            "hardware.asc",
            "hardware.bin",
            "hardware.dot",
            "hardware.json",
            "hardware.pnr",
            "hardware.svg",
            "main_tb.vcd",
        ]

        sb.write_default_apio_ini()

        for legacy_file in legacy_files:
            sb.write_file(legacy_file, "dummy text")
            assert Path(legacy_file).exists()

        result = sb.invoke_apio_cmd(apio, "clean")
        assert result.exit_code == 0, result.output

        for legacy_file in legacy_files:
            assert f"Removed {legacy_file}" in result.output
            assert not Path(legacy_file).exists()
