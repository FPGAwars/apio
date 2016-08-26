import pytest
from click.testing import CliRunner


@pytest.fixture(scope="module")
def clirunner():
    return CliRunner()


@pytest.fixture(scope="session")
def validate_cliresult():
    def decorator(result):
        assert result.exit_code == 0
        assert not result.exception
        assert "error" not in result.output.lower()
    return decorator


def pytest_addoption(parser):
    parser.addoption('--offline', action='store_true',
                     help='Run tests in offline mode')


@pytest.fixture
def offline(request):
    return request.config.getoption("--offline")
