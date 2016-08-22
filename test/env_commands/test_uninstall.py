import apio
from click.testing import CliRunner


def test_apio_uninstall_list():
    runner = CliRunner()
    result = runner.invoke(apio.uninstall, ['--list'])
    assert result.exit_code == 0
