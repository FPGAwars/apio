"""
  Test different "apio" commands
"""

from os import listdir, chdir
from os.path import getsize
from pathlib import Path
from test.conftest import ApioRunner
import pytest

# -- Entry point for apio commands.
from apio.commands.clean import cli as apio_clean
from apio.commands.graph import cli as apio_graph
from apio.commands.test import cli as apio_test
from apio.commands.report import cli as apio_report
from apio.commands.lint import cli as apio_lint
from apio.commands.build import cli as apio_build
from apio.commands.packages import cli as apio_packages
from apio.commands.examples import cli as apio_examples


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

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project directory.
        sb.proj_dir.mkdir()
        if not remote_proj_dir:
            chdir(sb.proj_dir)

        # -- In remote project dir mode we don't step into the project dir
        # -- and pass it as an arg.
        proj_arg = ["-p", str(sb.proj_dir)] if remote_proj_dir else []

        # -- 'apio packages --install --verbose'
        result = sb.invoke_apio_cmd(
            apio_packages, ["--install", "--verbose"] + proj_arg
        )
        sb.assert_ok(result)
        assert "'examples' installed successfully" in result.output
        assert "'oss-cad-suite' installed successfully" in result.output
        assert listdir(sb.packages_dir / "examples")
        assert listdir(sb.packages_dir / "tools-oss-cad-suite")

        # -- the project directory should be empty.
        assert not listdir(sb.proj_dir)

        # -- 'apio examples --fetch-files <example>``
        result = sb.invoke_apio_cmd(
            apio_examples,
            ["--fetch-files", example] + proj_arg,
        )
        sb.assert_ok(result)
        assert f"Copying {example} example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize(sb.proj_dir / "apio.ini")

        # -- Remember the original list of project files.
        project_files = listdir(sb.proj_dir)

        # -- 'apio build'
        result = sb.invoke_apio_cmd(apio_build, proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / "_build" / binary)

        # -- 'apio build' (no change)
        result = sb.invoke_apio_cmd(apio_build, proj_arg)
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
        result = sb.invoke_apio_cmd(apio_build, proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert "yosys" in result.output

        # -- 'apio lint'
        result = sb.invoke_apio_cmd(apio_lint, proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / "_build/hardware.vlt")

        # -- 'apio test'
        result = sb.invoke_apio_cmd(apio_test, proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / f"_build/{testbench}.out")
        assert getsize(sb.proj_dir / f"_build/{testbench}.vcd")

        # -- 'apio report'
        result = sb.invoke_apio_cmd(apio_report, proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert report_item in result.output
        assert getsize(sb.proj_dir / "_build/hardware.pnr")

        # -- 'apio graph'
        result = sb.invoke_apio_cmd(apio_graph, proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize(sb.proj_dir / "_build/hardware.dot")
        assert getsize(sb.proj_dir / "_build/hardware.svg")

        # -- 'apio clean'
        result = sb.invoke_apio_cmd(apio_clean, proj_arg)
        sb.assert_ok(result)
        assert "SUCCESS" in result.output
        assert not Path(sb.proj_dir / "_build").exists()

        # -- Here we should have only the original project files.
        assert set(listdir(sb.proj_dir)) == set(project_files)


def test_project_ice40_local_dir(apio_runner: ApioRunner):
    """Tests building and testing an ice40 project as the current working
    dir."""

    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="alhambra-ii/ledon",
        testbench="ledon_tb",
        binary="hardware.bin",
        report_item="ICESTORM_LC:",
    )


def test_project_ice40_remote_dir(apio_runner: ApioRunner):
    """Tests building and testing an ice40 project from a remote dir, using
    the -p option."""
    _test_project(
        apio_runner,
        remote_proj_dir=True,
        example="alhambra-ii/ledon",
        testbench="ledon_tb",
        binary="hardware.bin",
        report_item="ICESTORM_LC:",
    )


def test_project_ecp5_local_dir(apio_runner: ApioRunner):
    """Tests building and testing an ecp5 project as the current working dir"""
    _test_project(
        apio_runner,
        remote_proj_dir=False,
        example="ColorLight-5A-75B-V8/Ledon",
        testbench="ledon_tb",
        binary="hardware.bit",
        report_item="ALU54B:",
    )


def test_project_ecp5_remote_dir(apio_runner: ApioRunner):
    """Tests building and testing an ecp5 project from a remote directory."""
    _test_project(
        apio_runner,
        remote_proj_dir=True,
        example="ColorLight-5A-75B-V8/Ledon",
        testbench="ledon_tb",
        binary="hardware.bit",
        report_item="ALU54B:",
    )
