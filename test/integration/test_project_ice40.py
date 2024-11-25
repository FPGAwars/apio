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


# R0801: Similar lines in 2 files
# pylint: disable=R0801
def test_project_ice40(apio_runner: ApioRunner):
    """Tests building and testing a project."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if apio_runner.offline_flag:
        pytest.skip("requires internet connection")

    with apio_runner.in_disposable_temp_dir():

        # -- Config the apio test environment.
        proj_dir, _, packages_dir = apio_runner.setup_env()

        # -- Create and change to project dir.
        proj_dir.mkdir(exist_ok=False)
        chdir(proj_dir)

        # -- Install all packages
        result = apio_runner.invoke(apio_packages, ["--install", "--verbose"])
        apio_runner.assert_ok(result)
        assert "'examples' installed successfully" in result.output
        assert "'oss-cad-suite' installed successfully" in result.output
        assert listdir(packages_dir / "examples")
        assert listdir(packages_dir / "tools-oss-cad-suite")

        # -- The current proj directory should be still empty
        assert not listdir(".")

        # -- Fetch example files to current directory
        result = apio_runner.invoke(
            apio_examples,
            ["--fetch-files", "Alhambra-II/ledon"],
        )
        apio_runner.assert_ok(result)
        assert "Copying Alhambra-II/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("apio.ini")

        # -- Remember the list of project files.
        project_files = listdir(".")

        # -- Build the project.
        result = apio_runner.invoke(apio_build)
        apio_runner.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize("_build/hardware.bin")

        # -- Lint
        result = apio_runner.invoke(apio_lint)
        apio_runner.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize("_build/hardware.vlt")

        # -- Test
        result = apio_runner.invoke(apio_test)
        apio_runner.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize("_build/ledon_tb.out")
        assert getsize("_build/ledon_tb.vcd")

        # -- Report
        result = apio_runner.invoke(apio_report)
        apio_runner.assert_ok(result)
        assert "SUCCESS" in result.output
        assert "ICESTORM_LC:" in result.output
        assert getsize("_build/hardware.pnr")

        # -- Graph svg
        result = apio_runner.invoke(apio_graph)
        apio_runner.assert_ok(result)
        assert "SUCCESS" in result.output
        assert getsize("_build/hardware.dot")
        assert getsize("_build/hardware.svg")

        # -- Clean
        result = apio_runner.invoke(apio_clean)
        apio_runner.assert_ok(result)
        assert "SUCCESS" in result.output
        assert not Path("_build").exists()

        # -- Check that we have exactly the original project files,
        assert set(listdir(".")) == set(project_files)
