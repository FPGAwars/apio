import pytest

from os import getcwd, listdir, mkdir
from os.path import join, isfile, isdir, getsize

import click

from apio.commands.install import cli as cmd_install
from apio.commands.uninstall import cli as cmd_uninstall
from apio.commands.init import cli as cmd_init
from apio.commands.upload import cli as cmd_upload
from apio.commands.examples import cli as cmd_examples


def validate_files_leds(apioproject_dir):
    path = join(apioproject_dir, 'leds.v')
    assert isfile(path) and getsize(path) > 0


def validate_dir_leds(apioproject_dir):
    path = join(apioproject_dir, 'leds')
    assert isdir(path) and len(listdir(path)) > 0


def test_complete(clirunner, validate_cliresult, configenv, offline):
    if offline:
        pytest.skip('requires internet connection')

    with clirunner.isolated_filesystem():
        configenv()

        # apio uninstall examples
        result = clirunner.invoke(
            cmd_uninstall, ['examples'], input='y')
        assert 'Do you want to continue?' in result.output
        assert 'Error: package \'examples\' is not installed' in result.output

        # apio install examples@X
        result = clirunner.invoke(cmd_install, ['examples@X'])
        assert 'Warning: package \'examples\' version X' in result.output
        assert 'does not match the semantic version' in result.output

        # apio install examples@0.0.7
        result = clirunner.invoke(cmd_install, ['examples@0.0.7'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        if click.__version__ != '7.0':
            assert 'Downloading' in result.output
            assert 'Unpacking' in result.output
        assert 'has been successfully installed!' in result.output

        # apio install examples
        result = clirunner.invoke(cmd_install, ['examples'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        if click.__version__ != '7.0':
            assert 'Downloading' in result.output
            assert 'Unpacking' in result.output
        assert 'has been successfully installed!' in result.output

        # apio install examples
        result = clirunner.invoke(cmd_install, ['examples'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        assert 'Already installed. Version ' in result.output

        # apio install examples -p windows
        result = clirunner.invoke(cmd_install, [
            'examples', '--platform', 'windows', '--force'])
        validate_cliresult(result)
        assert 'Installing examples package' in result.output
        if click.__version__ != '7.0':
            assert 'Downloading' in result.output
            assert 'Unpacking' in result.output
        assert 'has been successfully installed!' in result.output

        # apio install --list
        result = clirunner.invoke(cmd_install, ['--list'])
        validate_cliresult(result)

        # apio init --board icezum
        result = clirunner.invoke(cmd_init, ['--board', 'icezum'])
        validate_cliresult(result)
        assert 'Creating apio.ini file ...' in result.output
        assert 'has been successfully created!' in result.output

        # apio upload
        result = clirunner.invoke(cmd_upload)
        assert result.exit_code == 1

        # apio examples --list
        result = clirunner.invoke(cmd_examples, ['--list'])
        validate_cliresult(result)
        assert 'leds' in result.output
        assert 'icezum' in result.output

        # apio examples --files missing_example
        result = clirunner.invoke(cmd_examples, ['--files', 'missing_example'])
        validate_cliresult(result)
        assert 'Warning: this example does not exist' in result.output

        # apio examples --files leds
        result = clirunner.invoke(cmd_examples, ['--files', 'leds'])
        validate_cliresult(result)
        assert 'Copying leds example files ...' in result.output
        assert 'have been successfully created!' in result.output
        validate_files_leds(getcwd())

        # apio examples --dir leds
        result = clirunner.invoke(cmd_examples, ['--dir', 'leds'])
        validate_cliresult(result)
        assert 'Creating leds directory ...' in result.output
        assert 'has been successfully created!' in result.output
        validate_dir_leds(getcwd())

        # apio examples --dir leds
        result = clirunner.invoke(cmd_examples, ['--dir', 'leds'], input='y')
        validate_cliresult(result)
        assert 'Warning: leds directory already exists' in result.output
        assert 'Do you want to replace it?' in result.output
        assert 'Creating leds directory ...' in result.output
        assert 'has been successfully created!' in result.output
        validate_dir_leds(getcwd())

        dir_name = 'tmp'
        mkdir(dir_name)

        # apio examples --files leds --project-dir=tmp
        result = clirunner.invoke(
            cmd_examples, ['--files', 'leds', '--project-dir=tmp'])
        validate_cliresult(result)
        assert 'Copying leds example files ...' in result.output
        assert 'have been successfully created!' in result.output
        validate_files_leds(join(getcwd(), dir_name))

        # apio examples --dir leds --project-dir=tmp
        result = clirunner.invoke(
            cmd_examples, ['--dir', 'leds', '--project-dir=tmp'])
        validate_cliresult(result)
        assert 'Creating leds directory ...' in result.output
        assert 'has been successfully created!' in result.output
        validate_dir_leds(join(getcwd(), dir_name))

        # apio uninstall examples
        result = clirunner.invoke(cmd_uninstall, ['examples'], input='n')
        validate_cliresult(result)
        assert 'Abort!' in result.output

        # apio uninstall examples
        result = clirunner.invoke(cmd_uninstall, ['examples'], input='y')
        validate_cliresult(result)
        assert 'Uninstalling examples package' in result.output
        assert 'Do you want to continue?' in result.output
        assert 'has been successfully uninstalled!' in result.output
