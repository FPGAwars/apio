"""
Pytest 
TEST configuration file
"""

# os.environ: Access to environment variables
#   https://docs.python.org/3/library/os.html#os.environ
from os import environ
from pathlib import Path

import pytest

# -- Class for executing click commands
# https://click.palletsprojects.com/en/8.1.x/api/#click.testing.CliRunner
from click.testing import CliRunner

#-- Class for storing the results of executing a click command
# https://click.palletsprojects.com/en/8.1.x/api/#click.testing.Result
from click.testing import Result

# -- Debug mode on/off
DEBUG = True


@pytest.fixture(scope='module')
def clirunner():
    """Return a special oject for executing a click cli command"""
    return CliRunner()


@pytest.fixture(scope='session')
def configenv():
    """Return a function for configuring the apio test environment
       By default it is tested in a temporaly folder (in /tmp/xxxxx)
    """
    def decorator():
        # -- Set a strange directory for executing
        # -- apio: it contains spaces and unicode characters
        # -- for testing. It should work
        cwd = str(Path.cwd() / ' ñ')

        #-- Debug
        if DEBUG:
            print("")
            print("  --> configenv():")
            print(f"      apio working directory: {cwd}")

        #-- Set the apio home dir and apio packages dir to
        #-- this test folder
        environ['APIO_HOME_DIR'] = cwd
        environ['APIO_PKG_DIR'] = cwd
        environ['TESTING'] = ''

    return decorator


@pytest.fixture(scope='session')
def validate_cliresult():
    """Return a function for Checking if a given click command 
       has executed ok
    """

    def decorator(result : Result):
        """Check if the result is ok"""

        #-- It should return an exit code of 0: success
        assert result.exit_code == 0

        #-- There should be no exceptions raised
        assert not result.exception

        #-- The word 'error' should NOT appear on the standard output
        assert 'error' not in result.output.lower()

    return decorator


#-- More info: https://docs.pytest.org/en/7.1.x/example/simple.html
def pytest_addoption(parser:pytest.Parser):
    """Register the --offline command line option when invoking pytest
    """

    #-- Option: --offline
    #-- It is used by the function test that requieres
    #-- internet connnection for testing
    parser.addoption('--offline', action='store_true',
                     help='Run tests in offline mode')


@pytest.fixture
def offline(request):
    """Return the value of the offline parameter, given by the user
       when calling pytest
    """
    return request.config.getoption('--offline')
