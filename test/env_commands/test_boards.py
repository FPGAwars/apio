import apio


def test_apio_boards_list(clirunner):
    result = clirunner.invoke(apio.boards, ['--list'])
    assert result.exit_code == 0
