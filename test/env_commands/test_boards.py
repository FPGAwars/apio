from apio.commands.boards import cli as cmd_boards


def test_apio_boards_list(clirunner):
    result = clirunner.invoke(cmd_boards, ['--list'])
    assert result.exit_code == 0
