"""
Tests of project.py
"""

from test.conftest import ApioRunner
from apio.apio_context import ApioContext, ApioContextScope

# TODO: Add more tests.


def test_required_and_optionals(apio_runner: ApioRunner):
    """Tests the required and optional options."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    # -- Required.
                    "board": "alhambra-ii",
                    # -- Optional.
                    "top-module": "my_module",
                    "format-verible-options": "\n  --aaa bbb\n  --ccc ddd",
                    "yosys-synth-extra-options": "-dsp -xyz",
                }
            }
        )

        # -- We use ApioContext to instantiate the Project object.
        apio_ctx = ApioContext(
            scope=ApioContextScope.PROJECT_REQUIRED,
            project_dir_arg=sb.proj_dir,
        )
        project = apio_ctx.project

        # -- Verify the required args.
        assert project.get("board") == "alhambra-ii"

        # -- Verify the optional args.
        assert project.get("top-module") == "my_module"
        assert project.get_as_lines_list("format-verible-options") == [
            "--aaa bbb",
            "--ccc ddd",
        ]
        assert project.get("yosys-synth-extra-options") == "-dsp -xyz"

        # -- Try a few as dict lookup.
        assert project["board"] == "alhambra-ii"
        assert project["top-module"] == "my_module"


def test_required_only(apio_runner: ApioRunner):
    """Tests the required only options."""

    with apio_runner.in_sandbox() as sb:

        # -- Create an apio.ini.
        sb.write_apio_ini(
            {
                "[env:default]": {
                    "board": "alhambra-ii",
                }
            }
        )

        # -- We use ApioContext to instantiate the Project object.
        apio_ctx = ApioContext(
            scope=ApioContextScope.PROJECT_REQUIRED,
            project_dir_arg=sb.proj_dir,
        )
        project = apio_ctx.project

        # -- Verify the required args.
        assert project.get("board") == "alhambra-ii"

        # -- Verify the optional args
        assert project.get("top-module") == "main"
        assert project.get_as_lines_list("format-verible-options") is None
        assert project.get("yosys-synth-extra-options") is None

        # -- Verify optionals while specifying explicit defaults.
        assert (
            project.get_as_lines_list("format-verible-options", default=[])
            == []
        )
        assert project.get("yosys-synth-extra-options", "") == ""

        # -- Try a few as dict lookup.
        assert project["board"] == "alhambra-ii"
        assert project["top-module"] == "main"
