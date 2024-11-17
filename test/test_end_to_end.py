"""
  Test different "apio" commands
"""

import pathlib

import pytest

# -- Entry point for apio commands.
from apio.commands.packages import cli as cmd_packages
from apio.commands.create import cli as cmd_create
from apio.commands.upload import cli as cmd_upload
from apio.commands.examples import cli as cmd_examples


def validate_files_leds(folder):
    """Check that the ledon.v file is inside the given folder"""

    # -- File to check
    leds = folder / pathlib.Path("ledon.v")

    # -- The file should exists and have a size greather than 0
    assert leds.exists() and leds.stat().st_size > 0  # getsize(leds) > 0


def validate_dir_leds(folder=""):
    """Check that the leds folder has been created in the
    dir directory
    """

    # -- Get the leds path
    leds_dir = folder / pathlib.Path("Alhambra-II/ledon")

    # -- Calculate the numer of files in the leds folder
    nfiles = len(list(leds_dir.glob("*")))

    # -- The folder should exist, and it should
    # -- containe more than 0 files inside
    assert leds_dir.is_dir() and nfiles > 0


def test_end_to_end1(clirunner, validate_cliresult, configenv, offline):
    """Test the installation of the examples package"""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline:
        pytest.skip("requires internet connection")

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio packages --uninstall examples"
        result = clirunner.invoke(
            cmd_packages, ["--uninstall", "examples"], input="y"
        )
        assert "Do you want to uninstall 1 package?" in result.output
        assert "Package 'examples' was not installed" in result.output

        # -- Execute "apio packages --install examples@X"
        result = clirunner.invoke(cmd_packages, ["--install", "examples@X"])
        assert "Error: package not found" in result.output

        # -- Execute "apio packages --install examples@0.0.34"
        result = clirunner.invoke(
            cmd_packages, ["--install", "examples@0.0.34"]
        )
        validate_cliresult(result)
        assert "Installing package 'examples@" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # -- Execute "apio packages --install examples"
        result = clirunner.invoke(cmd_packages, ["--install", "examples"])
        validate_cliresult(result)
        assert "Installing package 'examples'" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # -- Execute "apio packages --install examples" again
        result = clirunner.invoke(cmd_packages, ["--install", "examples"])
        validate_cliresult(result)
        assert "Installing package 'examples'" in result.output
        assert "was already installed" in result.output

        # -- Execute
        # -- "apio packages
        # --    --install examples
        # --    --platform windows_amd64
        # --    --force"
        result = clirunner.invoke(
            cmd_packages,
            [
                "--install",
                "examples",
                "--platform",
                "windows_amd64",
                "--force",
            ],
        )
        validate_cliresult(result)
        assert "Installing package 'examples'" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # -- Execute "apio packages --install --list"
        result = clirunner.invoke(cmd_packages, ["--list"])
        assert result.exit_code == 0, result.output
        assert "No errors" in result.output
        assert "Installed packages:" in result.output
        assert "examples" in result.output


def test_end_to_end2(clirunner, validate_cliresult, configenv, offline):
    """Test more 'apio examples' commands"""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline:
        pytest.skip("requires internet connection")

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio create --board alhambra-ii"
        result = clirunner.invoke(cmd_create, ["--board", "alhambra-ii"])
        validate_cliresult(result)
        assert "Creating apio.ini file ..." in result.output
        assert "was created successfully" in result.output

        # -- Execute "apio upload"
        result = clirunner.invoke(cmd_upload)
        assert result.exit_code == 1, result.output
        assert "package 'oss-cad-suite' is not installed" in result.output

        # -- Execute "apio packages --install examples"
        result = clirunner.invoke(cmd_packages, ["--install", "examples"])
        validate_cliresult(result)
        assert "Installing package 'examples'" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # -- Execute "apio examples --list"
        result = clirunner.invoke(cmd_examples, ["--list"])
        validate_cliresult(result)
        assert "leds" in result.output
        assert "icezum" in result.output

        # -- Execute "apio examples --fetch-files missing_example"
        result = clirunner.invoke(
            cmd_examples, ["--fetch-files", "missing_example"]
        )
        assert result.exit_code == 1, result.output
        assert "Warning: this example does not exist" in result.output

        # -- Execute "apio examples --fetch-files Alhambra-II/ledon"
        result = clirunner.invoke(
            cmd_examples, ["--fetch-files", "Alhambra-II/ledon"]
        )
        validate_cliresult(result)
        assert "Copying Alhambra-II/ledon example files ..." in result.output
        assert "have been successfully created!" in result.output
        validate_files_leds(pathlib.Path())

        # -- Execute "apio examples --fetch-dir Alhambra-II/ledon"
        result = clirunner.invoke(
            cmd_examples, ["--fetch-dir", "Alhambra-II/ledon"]
        )
        validate_cliresult(result)
        assert "Creating Alhambra-II/ledon directory ..." in result.output
        assert "has been successfully created" in result.output
        validate_dir_leds()

        # -- Execute "apio examples --fetch-dir Alhambra-II/ledon"
        result = clirunner.invoke(
            cmd_examples, ["--fetch-dir", "Alhambra-II/ledon"], input="y"
        )
        validate_cliresult(result)
        assert (
            "Warning: Alhambra-II/ledon directory already exists"
            in result.output
        )
        assert "Do you want to replace it?" in result.output
        assert "Creating Alhambra-II/ledon directory ..." in result.output
        assert "has been successfully created" in result.output
        validate_dir_leds()


def test_end_to_end3(clirunner, validate_cliresult, configenv, offline):
    """Test more 'apio examples' commands"""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline:
        pytest.skip("requires internet connection")

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio packages --install examples"
        result = clirunner.invoke(cmd_packages, ["--install", "examples"])
        validate_cliresult(result)
        assert "Installing package 'examples'" in result.output
        assert "Download" in result.output
        assert "Package 'examples' installed successfully" in result.output

        # ------------------------------------------
        # -- Check the --project-dir parameter
        # ------------------------------------------
        # -- Create a tmp dir
        p = pathlib.Path("tmp/")
        p.mkdir(parents=True, exist_ok=True)

        # -- Execute "apio examples --fetch-files Alhambra-II/ledon
        # --                        --project-dir=tmp"
        result = clirunner.invoke(
            cmd_examples,
            ["--fetch-files", "Alhambra-II/ledon", "--project-dir=tmp"],
        )
        validate_cliresult(result)
        assert "Copying Alhambra-II/ledon example files ..." in result.output
        assert "have been successfully created!" in result.output

        # -- Check the files in the tmp folder
        validate_files_leds(p)

        # -- Execute
        # -- "apio examples --fetch-dir Alhambra-II/ledon --project-dir=tmp"
        result = clirunner.invoke(
            cmd_examples,
            ["--fetch-dir", "Alhambra-II/ledon", "--project-dir=tmp"],
        )
        validate_cliresult(result)
        assert "Creating Alhambra-II/ledon directory ..." in result.output
        assert "has been successfully created" in result.output
        validate_dir_leds("tmp")

        # -- Execute "apio packages --uninstall examples"
        result = clirunner.invoke(
            cmd_packages, ["--uninstall", "examples"], input="n"
        )
        assert result.exit_code != 0, result.output
        assert "User said no" in result.output

        # -- Execute "apio packages --uninstall examples"
        result = clirunner.invoke(
            cmd_packages, ["--uninstall", "examples"], input="y"
        )
        validate_cliresult(result)
        assert "Uninstalling package 'examples'" in result.output
        assert "Do you want to uninstall 1 package?" in result.output
        assert "Package 'examples' uninstalled successfuly" in result.output
