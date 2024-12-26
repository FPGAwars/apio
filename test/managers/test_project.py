"""
Tests of project.py
"""

from os import chdir
from test.conftest import ApioRunner
from apio.apio_context import ApioContext, ApioContextScope

# pylint: disable=fixme
# TODO: Add more tests.


def test_options(apio_runner: ApioRunner):
    """Tests the options access."""

    with apio_runner.in_sandbox() as sb:

        # -- Create and change to project dir.
        sb.proj_dir.mkdir()
        chdir(sb.proj_dir)

        # -- Create an apio.ini.
        sb.write_apio_ini(
            {
                "board": "alhambra-ii",
                "top-module": "main",
                "format-verible-options": "\n  --aaa bbb\n  --ccc ddd",
            }
        )

        # -- We use ApioContext to instantiate the Project object.
        apio_ctx = ApioContext(
            scope=ApioContextScope.PROJECT_REQUIRED,
            project_dir_arg=sb.proj_dir,
        )
        project = apio_ctx.project

        assert project.get("board") == "alhambra-ii"
        assert project.get("top-module") == "main"
        assert project.get_as_lines_list("format-verible-options") == [
            "--aaa bbb",
            "--ccc ddd",
        ]

        assert project["board"] == "alhambra-ii"
        assert project["top-module"] == "main"
