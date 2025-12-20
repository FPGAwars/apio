"""
Test various "apio" commands.
"""

import os
from os.path import getsize
from pathlib import Path
from tests.conftest import ApioRunner
from apio.commands.apio import apio_top_cli as apio


def test_project_with_legacy_board_id(apio_runner: ApioRunner):
    """Test a project that uses a legacy board id."""

    # -- We shared the apio home with the other tests in this file to speed
    # -- up apio package installation. Tests should not mutate the shared home
    # -- to avoid cross-interference between tests in this file.
    with apio_runner.in_sandbox() as sb:

        # -- Fetch an example of a board that has a legacy name.
        result = sb.invoke_apio_cmd(
            apio, ["examples", "fetch", "ice40-hx8k/leds"]
        )
        sb.assert_result_ok(result)

        # -- Run 'apio build'
        result = sb.invoke_apio_cmd(apio, ["build"])
        sb.assert_result_ok(result)

        # -- Modify the apio.ini to have the legacy board id
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "iCE40-HX8K",
                    "top-module": "leds",
                }
            }
        )

        # -- Run 'apio clean'
        result = sb.invoke_apio_cmd(apio, ["clean"])
        sb.assert_result_ok(result)

        # -- Run 'apio build' again. It should also succeed.
        result = sb.invoke_apio_cmd(apio, ["build"])
        sb.assert_result_ok(result)


def _test_project(
    apio_runner: ApioRunner,
    *,
    remote_proj_dir: bool,
    example: str,
    testbench_file: str,
    bitstream: str,
    report_item: str,
):
    """A common project integration test. Invoked per each tested
    architecture.
    """

    # pylint: disable=too-many-arguments
    # pylint: disable=too-many-statements

    # -- Extract the base name of the testbench file
    testbench, _ = os.path.splitext(testbench_file)

    # -- We shared the apio home with the other tests in this file to speed
    # -- up apio package installation. Tests should not mutate the shared home
    # -- to avoid cross-interference between tests in this file.
    with apio_runner.in_sandbox() as sb:

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
        args = ["examples", "fetch", example] + dst_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert f"Copying {example} example files" in result.output
        assert "fetched successfully" in result.output
        assert getsize(sb.proj_dir / "apio.ini")

        # -- Remember the original list of project files.
        project_files = os.listdir(sb.proj_dir)

        # -- 'apio build'
        args = ["build"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert "yosys -p" in result.output

        assert getsize(sb.proj_dir / "_build/default" / bitstream)

        # -- 'apio build' (no change)
        args = ["build"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert "yosys -p" not in result.output

        # -- Modify apio.ini
        apio_ini_lines = sb.read_file(
            sb.proj_dir / "apio.ini", lines_mode=True
        )
        apio_ini_lines.append(" ")
        sb.write_file(sb.proj_dir / "apio.ini", apio_ini_lines, exists_ok=True)

        # -- 'apio build'
        # -- Apio.ini modification should triggers a new build.
        args = ["build"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert "yosys -p" in result.output

        # -- 'apio lint'
        args = ["lint"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / "_build/default/hardware.vlt")

        # -- 'apio format'
        args = ["format"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)

        # -- 'apio format <testbench-file>'
        # -- This tests the project relative specification even when
        # -- the option --project-dir is used.
        args = ["format", testbench_file] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)

        # -- 'apio test'
        args = ["test"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / f"_build/default/{testbench}.out")
        assert getsize(sb.proj_dir / f"_build/default/{testbench}.vcd")
        # -- For issue https://github.com/FPGAwars/apio/issues/557
        assert "warning: Timing checks are not supported" not in result.output

        # -- 'apio clean'
        args = ["clean"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "Cleanup completed" in result.output
        assert not (sb.proj_dir / f"_build/default/{testbench}.out").exists()
        assert not (sb.proj_dir / f"_build/default/{testbench}.vcd").exists()

        # -- 'apio sim --no-gtkwave'
        args = ["sim", "--no-gtkwave"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / f"_build/default/{testbench}.out")
        assert getsize(sb.proj_dir / f"_build/default/{testbench}.vcd")
        # -- For issue https://github.com/FPGAwars/apio/issues/557
        assert "warning: Timing checks are not supported" not in result.output

        # -- 'apio clean'
        args = ["clean"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "Cleanup completed" in result.output
        assert not (sb.proj_dir / f"_build/default/{testbench}.out").exists()
        assert not (sb.proj_dir / f"_build/default/{testbench}.vcd").exists()

        # -- 'apio test <testbench-file>'
        args = ["test", testbench_file] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / f"_build/default/{testbench}.out")
        assert getsize(sb.proj_dir / f"_build/default/{testbench}.vcd")
        # -- For issue https://github.com/FPGAwars/apio/issues/557
        assert "warning: Timing checks are not supported" not in result.output

        # -- 'apio sim --no-gtkw <testbench-file>'
        args = ["sim", "--no-gtkwave", testbench_file] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / f"_build/default/{testbench}.out")
        assert getsize(sb.proj_dir / f"_build/default/{testbench}.vcd")
        # -- For issue https://github.com/FPGAwars/apio/issues/557
        assert "warning: Timing checks are not supported" not in result.output

        # -- 'apio clean'
        args = ["clean"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "Cleanup completed" in result.output
        assert not (sb.proj_dir / f"_build/default/{testbench}.out").exists()
        assert not (sb.proj_dir / f"_build/default/{testbench}.vcd").exists()

        # -- 'apio report'
        args = ["report"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert report_item in result.output
        assert "─────┐" in result.output  # Graphical table border
        assert getsize(sb.proj_dir / "_build/default/hardware.pnr")

        # -- 'apio graph -n'
        args = ["graph", "-n"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / "_build/default/graph.dot")
        assert getsize(sb.proj_dir / "_build/default/graph.svg")

        # -- 'apio clean'
        assert Path(sb.proj_dir / "_build/default").exists()
        args = ["clean"] + proj_arg
        result = sb.invoke_apio_cmd(apio, args)
        sb.assert_result_ok(result)
        assert "Cleanup completed" in result.output
        assert not Path(sb.proj_dir / "_build/default").exists()

        # -- Here we should have only the original project files.
        assert set(os.listdir(sb.proj_dir)) == set(project_files)


# NOTE: We use the alhambra-ii/bcd-counter example because it uses
# subdirectories. This increases the test coverage.
def test_project_ice40_local_dir(apio_runner: ApioRunner):
    """Tests building and testing an ice40 project as the current working
    dir."""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="alhambra-ii/bcd-counter",
        testbench_file="main_tb.v",
        bitstream="hardware.bin",
        report_item="ICESTORM_LC",
    )


def test_project_ice40_remote_dir(apio_runner: ApioRunner):
    """Tests building and testing an ice40 project from a remote dir, using
    the -p option."""
    _test_project(
        apio_runner,
        remote_proj_dir=True,
        example="alhambra-ii/bcd-counter",
        testbench_file="main_tb.v",
        bitstream="hardware.bin",
        report_item="ICESTORM_LC",
    )


def test_project_ice40_system_verilog(apio_runner: ApioRunner):
    """Tests building and testing an ice40 project that contains system
    verilog files."""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="alhambra-ii/bcd-counter-sv",
        testbench_file="main_tb.sv",
        bitstream="hardware.bin",
        report_item="ICESTORM_LC",
    )


def test_project_ecp5_local_dir(apio_runner: ApioRunner):
    """Tests building and testing an ecp5 project as the current working dir"""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="colorlight-5a-75b-v8/ledon",
        testbench_file="ledon_tb.v",
        bitstream="hardware.bit",
        report_item="ALU54B",
    )


def test_project_ecp5_remote_dir(apio_runner: ApioRunner):
    """Tests building and testing an ecp5 project from a remote directory."""
    _test_project(
        apio_runner,
        remote_proj_dir=True,
        example="colorlight-5a-75b-v8/ledon",
        testbench_file="ledon_tb.v",
        bitstream="hardware.bit",
        report_item="ALU54B",
    )


def test_project_ecp5_system_verilog(apio_runner: ApioRunner):
    """Tests building and testing an ecp5 project that contains system
    verilog files."""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="colorlight-5a-75b-v8/ledon-sv",
        testbench_file="ledon_tb.sv",
        bitstream="hardware.bit",
        report_item="ALU54B",
    )


def test_project_gowin_local_dir(apio_runner: ApioRunner):
    """Tests building and testing a gowin project as the current working dir"""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="sipeed-tang-nano-9k/blinky",
        testbench_file="blinky_tb.v",
        bitstream="hardware.fs",
        report_item="LUT4",
    )


def test_project_gowin_remote_dir(apio_runner: ApioRunner):
    """Tests building and testing a gowin project from a remote directory."""
    _test_project(
        apio_runner,
        remote_proj_dir=True,
        example="sipeed-tang-nano-9k/blinky",
        testbench_file="blinky_tb.v",
        bitstream="hardware.fs",
        report_item="LUT4",
    )


def test_project_gowin_system_verilog(apio_runner: ApioRunner):
    """Tests building and testing an gowin project that contains system
    verilog files."""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="sipeed-tang-nano-9k/blinky-sv",
        testbench_file="blinky_tb.sv",
        bitstream="hardware.fs",
        report_item="LUT4",
    )
