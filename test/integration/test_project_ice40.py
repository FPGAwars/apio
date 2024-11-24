"""
  Test different "apio" commands
"""

from os import listdir, chdir
from os.path import getsize
from pathlib import Path
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
def test_project_ice40(
    click_cmd_runner,
    setup_apio_test_env,
    assert_apio_cmd_ok,
    offline_flag,
):
    """Tests building and testing a project."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment.
        proj_dir, _, packages_dir = setup_apio_test_env()

        # -- Create and change to project dir.
        proj_dir.mkdir(exist_ok=False)
        chdir(proj_dir)

        # -- Install all packages
        result = click_cmd_runner.invoke(
            apio_packages, ["--install", "--verbose"]
        )
        assert_apio_cmd_ok(result)
        assert "'examples' installed successfully" in result.output
        assert "'oss-cad-suite' installed successfully" in result.output
        assert listdir(packages_dir / "examples")
        assert listdir(packages_dir / "tools-oss-cad-suite")

        # -- The current proj directory should be still empty
        assert not listdir(".")

        # -- Fetch example files to current directory
        result = click_cmd_runner.invoke(
            apio_examples,
            ["--fetch-files", "Alhambra-II/ledon"],
        )
        assert_apio_cmd_ok(result)
        assert "Copying Alhambra-II/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("apio.ini")

        # -- Remember the list of project files.
        project_files = listdir(".")

        # -- Build the project.
        result = click_cmd_runner.invoke(apio_build)
        assert_apio_cmd_ok(result)
        assert "SUCCESS" in result.output
        assert getsize("_build/hardware.bin")

        # -- Lint
        result = click_cmd_runner.invoke(apio_lint)
        assert_apio_cmd_ok(result)
        assert "SUCCESS" in result.output
        assert getsize("_build/hardware.vlt")

        # -- Test
        result = click_cmd_runner.invoke(apio_test)
        assert_apio_cmd_ok(result)
        assert "SUCCESS" in result.output
        assert getsize("_build/ledon_tb.out")
        assert getsize("_build/ledon_tb.vcd")

        # -- Report
        result = click_cmd_runner.invoke(apio_report)
        assert_apio_cmd_ok(result)
        assert "SUCCESS" in result.output
        assert "ICESTORM_LC:" in result.output
        assert getsize("_build/hardware.pnr")

        # -- Graph svg
        result = click_cmd_runner.invoke(apio_graph)
        assert_apio_cmd_ok(result)
        assert "SUCCESS" in result.output
        assert getsize("_build/hardware.dot")
        assert getsize("_build/hardware.svg")

        # -- Clean
        result = click_cmd_runner.invoke(apio_clean)
        assert_apio_cmd_ok(result)
        assert "SUCCESS" in result.output
        assert not Path("_build").exists()

        # -- Check that we have exactly the original project files,
        assert set(listdir(".")) == set(project_files)
