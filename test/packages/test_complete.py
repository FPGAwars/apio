"""
  Test different "apio" commands
"""

import pathlib

import pytest

#-- Entry point for the apio install, apio uninstall
#-- apio init, apio upload, apio examples
from apio.commands.install import cli as cmd_install
from apio.commands.uninstall import cli as cmd_uninstall
from apio.commands.init import cli as cmd_init
from apio.commands.upload import cli as cmd_upload
from apio.commands.examples import cli as cmd_examples


def validate_files_leds(folder):
    """Check that the ledon.v file is inside the given folder"""

    # -- File to check
    leds = folder / pathlib.Path('ledon.v')

    # -- The file should exists and have a size greather than 0
    assert leds.exists() and leds.stat().st_size > 0 #getsize(leds) > 0


def validate_dir_leds(folder=""):
    """Check that the leds folder has been created in the
    dir directory
    """

    #-- Get the leds path
    leds_dir = folder / pathlib.Path("Alhambra-II/ledon")

    # -- Calculate the numer of files in the leds folder
    nfiles = len(list(leds_dir.glob('*')))

    # -- The folder should exist, and it should
    # -- containe more than 0 files inside
    assert leds_dir.is_dir() and nfiles > 0


def test_complete(clirunner, validate_cliresult, configenv, offline):
    """Test the installation of the examples package"""

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline:
        pytest.skip('requires internet connection')

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio uninstall examples"
        result = clirunner.invoke(
            cmd_uninstall, ['examples'], input='y')
        assert 'Do you want to continue?' in result.output
        assert 'Error: package \'examples\' is not installed' in result.output

        # -- Execute "apio install examples@X"
        result = clirunner.invoke(cmd_install, ['examples@X'])
        assert 'Error: Package not found' in result.output

        # -- Execute "apio install examples@0.0.34"
        result = clirunner.invoke(cmd_install, ['examples@0.0.34'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        assert 'Download' in result.output
        assert 'has been successfully installed!' in result.output

        # -- Execute "apio install examples"
        result = clirunner.invoke(cmd_install, ['examples'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        assert 'Download' in result.output
        assert 'has been successfully installed!' in result.output

        # -- Execute "apio install examples" again
        result = clirunner.invoke(cmd_install, ['examples'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        assert 'Already installed. Version ' in result.output

        # -- Execute "apio install examples --platform windows --force"
        result = clirunner.invoke(cmd_install, [
            'examples', '--platform', 'windows', '--force'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        assert 'Download' in result.output
        assert 'has been successfully installed!' in result.output

        # -- Execute "apio install --list"
        result = clirunner.invoke(cmd_install, ['--list'])
        validate_cliresult(result)
        assert 'Installed packages:' in result.output
        assert 'examples' in result.output


def test_complete2(clirunner, validate_cliresult, configenv, offline):
    """Test more 'apio examples' commands """

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline:
        pytest.skip('requires internet connection')

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio init --board alhambra-ii"
        result = clirunner.invoke(cmd_init, ['--board', 'alhambra-ii'])
        validate_cliresult(result)
        assert 'Creating apio.ini file ...' in result.output
        assert 'has been successfully created!' in result.output

        # -- Execute "apio upload"
        result = clirunner.invoke(cmd_upload)
        assert result.exit_code == 1
        assert "package 'oss-cad-suite' is not installed" in result.output

        # -- Execute "apio install examples"
        result = clirunner.invoke(cmd_install, ['examples'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        assert 'Download' in result.output
        assert 'has been successfully installed!' in result.output

        # -- Execute "apio examples --list"
        result = clirunner.invoke(cmd_examples, ['--list'])
        validate_cliresult(result)
        assert 'leds' in result.output
        assert 'icezum' in result.output

        # -- Execute "apio examples --files missing_example"
        result = clirunner.invoke(cmd_examples, ['--files', 'missing_example'])
        assert result.exit_code == 1
        assert 'Warning: this example does not exist' in result.output

        # -- Execute "apio examples --files Alhambra-II/ledon"
        result = clirunner.invoke(cmd_examples, ['--files', 'Alhambra-II/ledon'])
        validate_cliresult(result)
        assert 'Copying Alhambra-II/ledon example files ...' in result.output
        assert 'have been successfully created!' in result.output
        validate_files_leds(pathlib.Path())

        # -- Execute "apio examples --dir Alhambra-II/ledon"
        result = clirunner.invoke(cmd_examples, ['--dir', 'Alhambra-II/ledon'])
        validate_cliresult(result)
        assert 'Creating Alhambra-II/ledon directory ...' in result.output
        assert 'has been successfully created!' in result.output
        validate_dir_leds()

        # -- Execute "apio examples --dir Alhambra-II/ledon"
        result = clirunner.invoke(cmd_examples, ['--dir', 'Alhambra-II/ledon'], input='y')
        validate_cliresult(result)
        assert 'Warning: Alhambra-II/ledon directory already exists' in result.output
        assert 'Do you want to replace it?' in result.output
        assert 'Creating Alhambra-II/ledon directory ...' in result.output
        assert 'has been successfully created!' in result.output
        validate_dir_leds()


def test_complete3(clirunner, validate_cliresult, configenv, offline):
    """Test more 'apio examples' commands """

    # -- If the option 'offline' is passed, the test is skip
    # -- (These tests require internet)
    if offline:
        pytest.skip('requires internet connection')

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio install examples"
        result = clirunner.invoke(cmd_install, ['examples'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        assert 'Download' in result.output
        assert 'has been successfully installed!' in result.output

        # ------------------------------------------
        # -- Check the --project-dir parameter
        # ------------------------------------------
        #-- Create a tmp dir
        p = pathlib.Path("tmp/")
        p.mkdir(parents=True, exist_ok=True)

        # -- Execute "apio examples --files Alhambra-II/ledon --project-dir=tmp"
        result = clirunner.invoke(
            cmd_examples, ['--files', 'Alhambra-II/ledon', '--project-dir=tmp'])
        validate_cliresult(result)
        assert 'Copying Alhambra-II/ledon example files ...' in result.output
        assert 'have been successfully created!' in result.output

        # -- Check the files in the tmp folder
        validate_files_leds(p)

        # -- Execute "apio examples --dir Alhambra-II/ledon --project-dir=tmp"
        result = clirunner.invoke(
            cmd_examples, ['--dir', 'Alhambra-II/ledon', '--project-dir=tmp'])
        validate_cliresult(result)
        assert 'Creating Alhambra-II/ledon directory ...' in result.output
        assert 'has been successfully created!' in result.output
        validate_dir_leds('tmp')

        # -- Execute "apio uninstall examples"
        result = clirunner.invoke(cmd_uninstall, ['examples'], input='n')
        validate_cliresult(result)
        assert 'Abort!' in result.output

        # -- Execute "apio uninstall examples"
        result = clirunner.invoke(cmd_uninstall, ['examples'], input='y')
        validate_cliresult(result)
        assert 'Uninstalling examples package' in result.output
        assert 'Do you want to continue?' in result.output
        assert 'has been successfully uninstalled!' in result.output
