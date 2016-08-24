import pytest
import os
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


@pytest.fixture(scope="module")
def isolated_apio_home(request, tmpdir_factory):
    home_dir = tmpdir_factory.mktemp(".apio")
    os.environ['APIO_HOME_DIR'] = str(home_dir)

    def fin():
        del os.environ['APIO_HOME_DIR']

    request.addfinalizer(fin)
    return home_dir
