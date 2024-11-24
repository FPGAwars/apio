"""
  Test different "apio" commands
"""

from os import listdir, chdir
from os.path import getsize
from pathlib import Path

import pytest

# -- Entry point for apio commands.
from apio.commands.raw import cli as apio_raw
from apio.commands.upgrade import cli as apio_upgrade
from apio.commands.system import cli as apio_system
from apio.commands.clean import cli as apio_clean
from apio.commands.graph import cli as apio_graph
from apio.commands.test import cli as apio_test
from apio.commands.report import cli as apio_report
from apio.commands.lint import cli as apio_lint
from apio.commands.build import cli as apio_build
from apio.commands.packages import cli as apio_packages
from apio.commands.examples import cli as apio_examples


def test_utilities(
    click_cmd_runner,
    setup_apio_test_env,
    assert_apio_cmd_ok,
    offline_flag,
):
    """Tests utility commands."""

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

        # -- Run 'apio upgrade'
        result = click_cmd_runner.invoke(apio_upgrade)
        assert_apio_cmd_ok(result)
        assert "Lastest Apio stable version" in result.output

        # -- Run 'apio system --info'
        result = click_cmd_runner.invoke(apio_system, ["--info"])
        assert_apio_cmd_ok(result)
        assert "Apio version" in result.output

        # -- Run 'apio raw --env "nextpnr-ice40 --help"
        result = click_cmd_runner.invoke(
            apio_raw, ["--env", "nextpnr-ice40 --help"], input="exit"
        )
        assert_apio_cmd_ok(result)


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


# # R0915: Too many statements (52/50) (too-many-statements)
# # pylint: disable=R0915
def test_packages(
    click_cmd_runner,
    setup_apio_test_env,
    assert_apio_cmd_ok,
    offline_flag,
):
    """Tests listing, installation and uninstallation of packages."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        proj_dir, _, packages_dir = setup_apio_test_env()

        # -- Create and change to project dir.
        proj_dir.mkdir(exist_ok=False)
        chdir(proj_dir)

        # -- List packages
        result = click_cmd_runner.invoke(apio_packages, ["--list"])
        assert result.exit_code == 0
        assert "No errors" in result.output
        assert "examples" in result.output
        assert "oss-cad-suite" in result.output

        # -- Packages dir doesn't exist yet.
        assert not packages_dir.exists()

        # -- Install the examples package. Package 'examples' should exist,
        # -- and package 'tools-oss-cad-suite' should not.
        result = click_cmd_runner.invoke(
            apio_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "Package 'examples' installed successfully" in result.output
        assert listdir(packages_dir / "examples/Alhambra-II")
        assert "tools-oss-cad-suite" not in listdir(packages_dir)

        # -- Install the reset of the packages.
        # -- Both 'examples' and 'tools-oss-cad-suite' should exist, and
        # -- maybe others, depending on the platform.
        result = click_cmd_runner.invoke(apio_packages, ["--install"])
        assert_apio_cmd_ok(result)
        assert "Package 'examples' installed successfully" not in result.output
        assert (
            "Package 'oss-cad-suite' installed successfully" in result.output
        )
        assert listdir(packages_dir / "examples/Alhambra-II")
        assert listdir(packages_dir / "tools-oss-cad-suite/bin")

        # -- Delete a file from the examples package, we will use it as an
        # -- indicator for the reinstallation of the package.
        marker_file = packages_dir / "examples/Alhambra-II/ledon/ledon.v"
        assert marker_file.is_file()
        marker_file.unlink()
        assert not marker_file.exists()

        # -- Install the examples packages without forcing.
        # -- This should not do anything since it's considered to be installed.
        result = click_cmd_runner.invoke(
            apio_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "was already install" in result.output
        assert "Package 'examples' installed" not in result.output
        assert not marker_file.exists()

        # -- Install the examples packages with forcing.
        # -- This should recover the file.
        result = click_cmd_runner.invoke(
            apio_packages, ["--install", "--force", "examples"]
        )
        assert_apio_cmd_ok(result)
        assert "Package 'examples' installed" in result.output
        assert marker_file.is_file()

        # -- Try to uninstall the 'examples' package without user approval.
        # -- should exit with an error message.
        assert "examples" in listdir(packages_dir)
        result = click_cmd_runner.invoke(
            apio_packages, ["--uninstall", "examples"], input="n"
        )
        assert result.exit_code == 1
        assert "User said no" in result.output
        assert "examples" in listdir(packages_dir)
        assert "tools-oss-cad-suite" in listdir(packages_dir)

        # -- Uninstall the examples package. It should delete the exemples
        # -- package and will live the rest.
        assert "examples" in listdir(packages_dir)
        result = click_cmd_runner.invoke(
            apio_packages, ["--uninstall", "examples"], input="y"
        )
        assert_apio_cmd_ok(result)
        assert "examples" not in listdir(packages_dir)
        assert "tools-oss-cad-suite" in listdir(packages_dir)

        # -- Uninstall all packages. This should uninstall also the
        # -- oss-cad-suite package.
        result = click_cmd_runner.invoke(
            apio_packages, ["--uninstall", "--sayyes"]
        )
        assert_apio_cmd_ok(result)
        assert "examples" not in listdir(packages_dir)
        assert "tools-oss-cad-suite" not in listdir(packages_dir)


def test_examples(
    click_cmd_runner,
    setup_apio_test_env,
    assert_apio_cmd_ok,
    offline_flag,
):
    """Tests the listing and fetching apio examples."""

    # -- If the option 'offline' is passed, the test is skip
    # -- (This test is slow and requires internet connectivity)
    if offline_flag:
        pytest.skip("requires internet connection")

    with click_cmd_runner.isolated_filesystem():

        # -- Config the apio test environment
        proj_dir, _, packages_dir = setup_apio_test_env()

        # -- Create and change to project dir.
        proj_dir.mkdir(exist_ok=False)
        chdir(proj_dir)

        # -- Install the examples package.
        result = click_cmd_runner.invoke(
            apio_packages, ["--install", "examples"]
        )
        assert_apio_cmd_ok(result)
        # assert "Installing package 'examples'" in result.output
        # assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output
        assert getsize(packages_dir / "examples/Alhambra-II/ledon/ledon.v")

        # -- List the examples
        result = click_cmd_runner.invoke(
            apio_examples,
            ["--list"],
        )
        assert_apio_cmd_ok(result)
        assert "Alhambra-II/ledon" in result.output

        # -- Fetch example files to current directory
        result = click_cmd_runner.invoke(
            apio_examples,
            ["--fetch-files", "Alhambra-II/ledon"],
        )
        assert_apio_cmd_ok(result)
        assert "Copying Alhambra-II/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("ledon.v")

        # -- Fetch example dir to current directory
        result = click_cmd_runner.invoke(
            apio_examples,
            ["--fetch-dir", "Alhambra-II/ledon"],
        )
        assert_apio_cmd_ok(result)
        assert "Creating Alhambra-II/ledon directory" in result.output
        assert "has been successfully created" in result.output
        assert getsize("Alhambra-II/ledon/ledon.v")

        # -- Fetch example files to another project dir
        result = click_cmd_runner.invoke(
            apio_examples,
            ["--fetch-files", "Alhambra-II/ledon", "--project-dir=./dir1"],
        )
        assert_apio_cmd_ok(result)
        assert "Copying Alhambra-II/ledon example files" in result.output
        assert "have been successfully created!" in result.output
        assert getsize("dir1/ledon.v")

        # -- Fetch example dir to another project dir
        result = click_cmd_runner.invoke(
            apio_examples,
            ["--fetch-dir", "Alhambra-II/ledon", "--project-dir=dir2"],
        )
        assert_apio_cmd_ok(result)
        assert "Creating Alhambra-II/ledon directory" in result.output
        assert "has been successfully created" in result.output
        assert getsize("dir2/Alhambra-II/ledon/ledon.v")
