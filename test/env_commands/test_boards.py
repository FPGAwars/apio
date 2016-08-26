from apio.commands.boards import cli as cmd_boards


def test_boards(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_boards)
    validate_cliresult(result)


def test_boards_list(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_boards, ['--list'])
    validate_cliresult(result)


def test_boards_fpgas(clirunner, validate_cliresult):
    result = clirunner.invoke(cmd_boards, ['--fpga'])
    validate_cliresult(result)
