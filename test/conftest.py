# -*- coding: utf-8 -*-

import pytest
from os import environ, getcwd, path
from click.testing import CliRunner


@pytest.fixture(scope='module')
def clirunner():
    return CliRunner()


@pytest.fixture(scope='session')
def validate_cliresult():
    def decorator(result):
        assert result.exit_code == 0
        assert not result.exception
        assert 'error' not in result.output.lower()
    return decorator


@pytest.fixture(scope='session')
def configenv():
    def decorator():
        cwd = path.join(getcwd(), ' ñ')
        environ['APIO_HOME_DIR'] = cwd
        environ['APIO_PKG_DIR'] = cwd
        environ['TESTING'] = ''
    return decorator


def pytest_addoption(parser):
    parser.addoption('--offline', action='store_true',
                     help='Run tests in offline mode')


@pytest.fixture
def offline(request):
    return request.config.getoption('--offline')
