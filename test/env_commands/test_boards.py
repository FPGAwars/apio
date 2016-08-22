import apio
from click.testing import CliRunner


def test_apio_boards_list():
    runner = CliRunner()
    result = runner.invoke(apio.boards, ['--list'])
    assert result.exit_code == 0
