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

CUSTOM_BOARDS = """
{
  "my_custom_board": {
    "name": "My Custom Board v3.1c",
    "fpga": "ice40up5k-sg48",
    "programmer": {
      "type": "iceprog"
    },
    "usb": {
      "vid": "0403",
      "pid": "6010"
    },
    "ftdi": {
      "desc": "My Custom Board"
    }
  }
}
"""


def test_boards_custom_board(apio_runner: ApioRunner):
    """Test boards listing with a custom boards.jsonc file."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox(shared_home=True) as sb:

        # -- Write an apio.ini file.
        sb.write_apio_ini({"board": "my_custom_board", "top-module": "main"})

        # -- Write a custom boards.jsonc file in the project's directory.
        sb.write_file("boards.jsonc", CUSTOM_BOARDS)

        # -- Execute "apio boards"
        result = sb.invoke_apio_cmd(apio, ["boards"])
        sb.assert_ok(result)
        # -- Note: pytest sees the piped version of the command's output.
        assert "Loading custom 'boards.jsonc'" in result.output
        assert "alhambra-ii" not in result.output
        assert "my_custom_board" in result.output
        assert "Total of 1 board" in result.output


def test_boards_list_ok(apio_runner: ApioRunner):
    """Test normal board listing with the apio's boards.jsonc."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox(shared_home=True) as sb:

        # -- Run 'apio boards'
        result = sb.invoke_apio_cmd(apio, ["boards"])
        sb.assert_ok(result)
        assert "Loading custom 'boards.jsonc'" not in result.output
        assert "FPGA-ID" not in result.output
        assert "alhambra-ii" in result.output
        assert "my_custom_board" not in result.output
        assert "Total of 1 board" not in result.output

        # -- Run 'apio boards -v'
        result = sb.invoke_apio_cmd(apio, ["boards", "-v"])
        sb.assert_ok(result)
        assert "Loading custom 'boards.jsonc'" not in result.output
        assert "FPGA-ID" in result.output
        assert "alhambra-ii" in result.output
        assert "my_custom_board" not in result.output
        assert "Total of 1 board" not in result.output


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_utilities(apio_runner: ApioRunner):
    """Tests apio utility commands."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_sandbox(shared_home=True) as sb:

        # -- Run 'apio upgrade'
        result = sb.invoke_apio_cmd(apio, ["upgrade"])
        sb.assert_ok(result)
        assert "Lastest Apio stable version" in result.output

        # -- Run 'apio raw  "nextpnr-ice40 --help"'
        result = sb.invoke_apio_cmd(
            apio, ["raw", "--", "nextpnr-ice40", "--help"]
        )
        sb.assert_ok(result)

        # -- Run 'apio raw -v'
        result = sb.invoke_apio_cmd(apio, ["raw", "-v"])
        sb.assert_ok(result)
        assert "Envirnment settings:" in result.output
        assert "YOSYS_LIB" in result.output


def test_project_with_legacy_board_name(apio_runner: ApioRunner):
    """Test a project that uses a legacy board name."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    # -- We shared the apio home with the other tests in this file to speed
    # -- up apio package installation. Tests should not mutate the shared home
    # -- to avoid cross-interferance between tests in this file.
    with apio_runner.in_sandbox(shared_home=True) as sb:

        # -- Fetch an example of a board that has a legacy name.
        result = sb.invoke_apio_cmd(
            apio,
            ["examples", "fetch", "ice40-hx8k/leds"],
        )
        sb.assert_ok(result)

        # -- Run 'apio build'
        result = sb.invoke_apio_cmd(apio, ["build"])
        sb.assert_ok(result)

        # -- Modify the apio.ini to have the legacy board name
        sb.write_apio_ini({"board": "iCE40-HX8K", "top-module": "leds"})

        # -- Run 'apio clean'
        result = sb.invoke_apio_cmd(apio, ["clean"])
        sb.assert_ok(result)

        # -- Run 'apio build' again. It should also succeeed.
        result = sb.invoke_apio_cmd(apio, ["build"])
        sb.assert_ok(result)


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
    bitstream: str,
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
        assert "fetched successfully" in result.output
        assert getsize(sb.proj_dir / "apio.ini")

        # -- Remember the original list of project files.
        project_files = os.listdir(sb.proj_dir)

        # -- 'apio build'
        result = sb.invoke_apio_cmd(apio, ["build"] + proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / "_build" / bitstream)

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
        # -- For issue https://github.com/FPGAwars/apio/issues/557
        assert "warning: Timing checks are not supported" not in result.output

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
        bitstream="hardware.bin",
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
        bitstream="hardware.bin",
        report_item="ICESTORM_LC:",
    )


def test_project_ecp5_local_dir(apio_runner: ApioRunner):
    """Tests building and testing an ecp5 project as the current working dir"""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="colorlight-5a-75b-v8/ledon",
        testbench="ledon_tb",
        bitstream="hardware.bit",
        report_item="ALU54B:",
    )


def test_project_ecp5_remote_dir(apio_runner: ApioRunner):
    """Tests building and testing an ecp5 project from a remote directory."""
    _test_project(
        apio_runner,
        remote_proj_dir=True,
        example="colorlight-5a-75b-v8/ledon",
        testbench="ledon_tb",
        bitstream="hardware.bit",
        report_item="ALU54B:",
    )


def test_project_gowin_local_dir(apio_runner: ApioRunner):
    """Tests building and testing a gowin project as the current working dir"""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="sipeed-tang-nano-4k/blinky",
        testbench="blinky_tb",
        bitstream="hardware.fs",
        report_item="ALU54D:",
    )


def test_project_gowin_remote_dir(apio_runner: ApioRunner):
    """Tests building and testing a gowin project from a remote directory."""
    _test_project(
        apio_runner,
        remote_proj_dir=True,
        example="sipeed-tang-nano-4k/blinky",
        testbench="blinky_tb",
        bitstream="hardware.fs",
        report_item="ALU54D:",
    )
