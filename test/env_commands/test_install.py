import apio
from click.testing import CliRunner


def test_apio_install_list():
    runner = CliRunner()
    result = runner.invoke(apio.install, ['--list'])
    assert result.exit_code == 0
