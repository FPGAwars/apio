"""
  Test different "apio" commands. These tests use installed apio packages
  and are slower than the offline tests at test/commands.
"""

import os
from os.path import getsize
from pathlib import Path
from test.conftest import ApioRunner
import pytest
from apio.commands.apio import cli as apio


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_utilities(apio_runner: ApioRunner):
    """Tests apio utility commands."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox(shared_home=True) as sb:

        # -- Install all packages. Not that since we run in a shared apio home,
        # -- the packages can be already installed by a previous test.
        result = sb.invoke_apio_cmd(apio, ["packages", "install"])
        sb.assert_ok(result)

        # -- Run 'apio upgrade'
        result = sb.invoke_apio_cmd(apio, ["upgrade"])
        sb.assert_ok(result)
        assert "Lastest Apio stable version" in result.output

        # -- Run 'apio raw  "nextpnr-ice40 --help"'
        result = sb.invoke_apio_cmd(
            apio, ["raw", "--", "nextpnr-ice40", "--help"]
        )
        sb.assert_ok(result)

        # -- Run 'apio raw --env'
        result = sb.invoke_apio_cmd(apio, ["raw", "--env"])
        sb.assert_ok(result)
        assert "Envirnment settings:" in result.output
        assert "YOSYS_LIB" in result.output


# Too many statements (60/50) (too-many-statements)
# pylint: disable=too-many-statements
# R0801: Similar lines in 2 files
# pylint: disable=R0801
# R0913: Too many arguments (6/5) (too-many-arguments)
# pylint: disable=too-many-arguments
def _test_project(
    apio_runner: ApioRunner,
    *,
    remote_proj_dir: bool,
    example: str,
    testbench: str,
    binary: str,
    report_item: str,
):
    """A common project integration test. Invoked per each tested
    architecture.
    """

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    # -- We shared the apio home with the other tests in this file to speed
    # -- up apio package installation. Tests should not mutate the shared home
    # -- to avoid cross-interferance between tests in this file.
    with apio_runner.in_sandbox(shared_home=True) as sb:

        # -- If testing from a remote dir, step out of the proj dir, and
        # -- use -p proj_dir arg.
        if remote_proj_dir:
            os.chdir(sb.sandbox_dir)
            sb.proj_dir.rmdir()
            proj_arg = ["-p", str(sb.proj_dir)]
            dst_arg = ["-d", str(sb.proj_dir)]
        else:
            proj_arg = []
            dst_arg = []

        # -- 'apio packages install'.
        # -- Note that since we used a sandbox with a shared home, the packages
        # -- may already been installed from a previous test in this file.
        result = sb.invoke_apio_cmd(apio, ["packages", "install"])
        sb.assert_ok(result)

        # -- If testing from a remote dir, the proj dir should not exist yet,
        # -- else, the project dir should be empty.
        if remote_proj_dir:
            assert not sb.proj_dir.exists()
        else:
            assert not os.listdir(sb.proj_dir)

        # -- 'apio examples fetch <example> -d <proj_dir>'
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch", example] + dst_arg,
        )
        sb.assert_ok(result)
        assert f"Copying {example} example files" in result.output
        assert "Fetched successfully" in result.output
        assert getsize(sb.proj_dir / "apio.ini")

        # -- Remember the original list of project files.
        project_files = os.listdir(sb.proj_dir)

        # -- 'apio build'
        result = sb.invoke_apio_cmd(apio, ["build"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / "_build" / binary)

        # -- 'apio build' (no change)
        result = sb.invoke_apio_cmd(apio, ["build"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert "yosys" not in result.output

        # -- Modify apio.ini
        apio_ini_lines = sb.read_file(
            sb.proj_dir / "apio.ini", lines_mode=True
        )
        apio_ini_lines.append(" ")
        sb.write_file(sb.proj_dir / "apio.ini", apio_ini_lines, exists_ok=True)

        # -- 'apio build'
        # -- Apio.ini modification should triggers a new build.
        result = sb.invoke_apio_cmd(apio, ["build"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert "yosys" in result.output

        # -- 'apio lint'
        result = sb.invoke_apio_cmd(apio, ["lint"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / "_build/hardware.vlt")

        # -- 'apio format'
        result = sb.invoke_apio_cmd(apio, ["format"] + proj_arg)
        sb.assert_ok(result)

        # -- 'apio test'
        result = sb.invoke_apio_cmd(apio, ["test"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / f"_build/{testbench}.out")
        assert getsize(sb.proj_dir / f"_build/{testbench}.vcd")

        # -- 'apio clean'
        result = sb.invoke_apio_cmd(apio, ["clean"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert not (sb.proj_dir / f"_build/{testbench}.out").exists()
        assert not (sb.proj_dir / f"_build/{testbench}.vcd").exists()

        # -- 'apio test <testbench-file>'
        result = sb.invoke_apio_cmd(
            apio, ["test", testbench + ".v"] + proj_arg
        )
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / f"_build/{testbench}.out")
        assert getsize(sb.proj_dir / f"_build/{testbench}.vcd")

        # -- 'apio report'
        result = sb.invoke_apio_cmd(apio, ["report"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert report_item in result.output
        assert getsize(sb.proj_dir / "_build/hardware.pnr")

        # -- 'apio graph'
        result = sb.invoke_apio_cmd(apio, ["graph"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / "_build/hardware.dot")
        assert getsize(sb.proj_dir / "_build/hardware.svg")

        # -- 'apio clean'
        result = sb.invoke_apio_cmd(apio, ["clean"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert not Path(sb.proj_dir / "_build").exists()

        # -- Here we should have only the original project files.
        assert set(os.listdir(sb.proj_dir)) == set(project_files)


def test_project_ice40_local_dir(apio_runner: ApioRunner):
    """Tests building and testing an ice40 project as the current working
    dir."""

    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="alhambra-ii/bcd-counter",
        testbench="main_tb",
        binary="hardware.bin",
        report_item="ICESTORM_LC:",
    )


def test_project_ice40_remote_dir(apio_runner: ApioRunner):
    """Tests building and testing an ice40 project from a remote dir, using
    the -p option."""
    _test_project(
        apio_runner,
        remote_proj_dir=True,
        example="alhambra-ii/bcd-counter",
        testbench="main_tb",
        binary="hardware.bin",
        report_item="ICESTORM_LC:",
    )


def test_project_ecp5_local_dir(apio_runner: ApioRunner):
    """Tests building and testing an ecp5 project as the current working dir"""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="colorlight-5a-75b-v8/ledon",
        testbench="ledon_tb",
        binary="hardware.bit",
        report_item="ALU54B:",
    )


def test_project_ecp5_remote_dir(apio_runner: ApioRunner):
    """Tests building and testing an ecp5 project from a remote directory."""
    _test_project(
        apio_runner,
        remote_proj_dir=True,
        example="colorlight-5a-75b-v8/ledon",
        testbench="ledon_tb",
        binary="hardware.bit",
        report_item="ALU54B:",
    )
