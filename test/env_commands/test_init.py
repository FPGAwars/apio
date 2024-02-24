"""
  Test for the "apio init" command
"""
import pathlib
from os.path import isfile, getsize

# -- apio init entry point
from apio.commands.init import cli as cmd_init


def validate_apio_ini():
    """Check that the apio.ini file has been created in the
    current directory
    """

    #-- Get the apio.ini path
    apio_ini = pathlib.Path("apio.ini")

    # -- The file should exist with a length
    # -- greather than zero
    assert isfile(apio_ini) and getsize(apio_ini) > 0


def validate_scons():
    """Check that the SConstruct file has been created in the
       current directory
    """
     #-- Get the SConstruct file
    scons_file = pathlib.Path("SConstruct")

    # -- The file should exist with a length
    # -- greather than zero
    assert isfile(scons_file) and getsize(scons_file) > 0


def test_init(clirunner, configenv, validate_cliresult):
    """Test "apio init" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio init"
        result = clirunner.invoke(cmd_init)
        validate_cliresult(result)

        # -- Execute "apio init --board missed_board"
        result = clirunner.invoke(cmd_init, ['--board', 'missed_board'])
        assert result.exit_code == 1
        assert 'Error: no such board' in result.output

        # -- Execute "apio init --board alhambra-ii"
        result = clirunner.invoke(cmd_init, ['--board', 'icezum'])
        validate_cliresult(result)

        # -- Check that the apio.ini files has been created
        validate_apio_ini()
        assert 'Creating apio.ini file ...' in result.output
        assert 'has been successfully created!' in result.output

        # -- Execute "apio init --board alhambra-ii" again
        result = clirunner.invoke(cmd_init, ['--board', 'icezum'], input='y')
        validate_cliresult(result)

        # -- Check the apio.ini file exists
        validate_apio_ini()

        # -- Check the new behaviour: apio.ini already exists!
        assert 'Warning' in result.output
        assert 'file already exists' in result.output
        assert 'Do you want to replace it?' in result.output
        assert 'has been successfully created!' in result.output


def test_init_scons(clirunner, configenv, validate_cliresult):
    """Test "apio init --scons" with different parameters"""

    with clirunner.isolated_filesystem():

        # -- Config the environment (conftest.configenv())
        configenv()

        # -- Execute "apio init --scons"
        result = clirunner.invoke(cmd_init, ['--scons'])
        validate_cliresult(result)

        # -- Check that the Sconstruct files exists
        validate_scons()
        assert 'Creating SConstruct file ...' in result.output
        assert 'has been successfully created!' in result.output

        # -- Execute "apio init --scons" again
        result = clirunner.invoke(cmd_init, ['--scons'], input='y')
        validate_cliresult(result)

        # -- Check that the Sconstruct files exists
        validate_scons()
        assert 'Warning' in result.output
        assert 'file already exists' in result.output
        assert 'Do you want to replace it?' in result.output
        assert 'has been successfully created!' in result.output

        # ------------------------------------------
        # -- Check the --project-dir parameter
        # ------------------------------------------
        #-- Create a tmp dir
        p = pathlib.Path("tmp/")
        p.mkdir(parents=True, exist_ok=True)

        # -- Execute "apio init --scons --project-dir=tmp"
        result = clirunner.invoke(cmd_init, ['--scons', '--project-dir=tmp'])
        validate_cliresult(result)

        # -- Check that the Sconstruct files exists
        validate_scons()
        assert 'Creating SConstruct file ...' in result.output
        assert 'has been successfully created!' in result.output
