"""Test for the "apio clean" command."""

import os
from pathlib import Path
from test.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_clean(apio_runner: ApioRunner):
    """Tests the 'apio clean' with two envs. It should delete _build."""

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

        sb.write_file("_build/env1/hardware.out", "dummy text")
        sb.write_file("_build/env2/hardware.out", "dummy text")

        assert Path("_build/env1/hardware.out").exists()
        assert Path("_build/env2/hardware.out").exists()

        result = sb.invoke_apio_cmd(apio, ["clean"])

        sb.assert_result_ok(result)
        assert "Removed _build" in result.output
        assert not Path("_build").exists()


def test_clean_from_remote_dir(apio_runner: ApioRunner):
    """Tests the 'apio clean' with two envs. It should delete _build."""

    with apio_runner.in_sandbox() as sb:

        # -- Cache directories values.
        proj_dir: Path = sb.proj_dir
        remote_dir: Path = sb.sandbox_dir

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

        sb.write_file("_build/env1/hardware.out", "dummy text")
        sb.write_file("_build/env2/hardware.out", "dummy text")

        assert Path("_build/env1/hardware.out").exists()
        assert Path("_build/env2/hardware.out").exists()

        # -- Run the clean command from a remote dir.
        os.chdir(remote_dir)
        assert not Path("apio.ini").exists()
        result = sb.invoke_apio_cmd(
            apio, ["clean", "--project-dir", str(proj_dir)]
        )
        sb.assert_result_ok(result)
        assert "Removed _build" in result.output
        os.chdir(proj_dir)
        assert not Path("_build").exists()


def test_clean_no_build(apio_runner: ApioRunner):
    """Tests the 'apio clean' command with nothing to delete."""

    with apio_runner.in_sandbox() as sb:

        sb.write_default_apio_ini()

        assert not Path("_build").exists()

        result = sb.invoke_apio_cmd(apio, ["clean"])
        sb.assert_result_ok(result)
        assert "Removed" not in result.output
        assert "Already clean" in result.output


def test_clean_legacy_files(apio_runner: ApioRunner):
    """Tests that 'apio clean' deletes also legacy files that may have been
    left in the project dir by apio version before 1.x.x.
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

        result = sb.invoke_apio_cmd(apio, ["clean"])
        sb.assert_result_ok(result)

        for legacy_file in legacy_files:
            assert f"Removed {legacy_file}" in result.output
            assert not Path(legacy_file).exists()
