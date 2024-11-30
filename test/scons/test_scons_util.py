"""
Tests of scons_util.py
"""

from os.path import isfile, exists
from pathlib import Path
from typing import Dict
from test.conftest import ApioRunner
import pytest
from SCons.Script.SConscript import SConsEnvironment
import SCons.Script.SConsOptions
from SCons.Node.FS import FS, File
import SCons.Node.FS
import SCons.Environment
import SCons.Defaults
import SCons.Script.Main
from SCons.Script import SetOption
from pytest import LogCaptureFixture
from apio.scons.scons_util import (
    make_verilog_src_scanner,
    has_testbench_name,
    is_verilog_src,
    create_construction_env,
    get_args,
    arg_str,
    arg_bool,
    is_windows,
    force_colors,
    set_up_cleanup,
    map_params,
    fatal_error,
    error,
    warning,
    info,
    msg,
    get_constraint_file,
    get_programmer_cmd,
    make_verilator_config_builder,
    get_source_files,
)

DEPENDECIES_TEST_TEXT = """
// Test file
parameter v771499 = "v771499.list"
`include "apio_testing.vh"
parameter v771499 = "v771499.list"
`include "apio_testing.v
"""


class SconsHacks:
    """A collection of staticmethods that encapsulate scons access outside of
    the official scons API. Hopefully this will not be too difficult to adapt
    in future versions of SCons."""

    @staticmethod
    def reset_scons_state() -> None:
        """Reset the relevant SCons global variables. וUnfurtunally scons
        uses a few global variables to hold its state. This works well in
        normal operation where an scons process contains a single scons
        session but with pytest testing, where multiple independent tests
        are running in the same process, we need to reset though variables
        before each test."""

        # -- The Cons.Script.Main.OptionsParser variables contains the command
        # -- line options of scons. We reset them here and tests can access
        # -- them using SetOption() and GetOption().

        parser = SCons.Script.SConsOptions.Parser("my_fake_version")
        values = SCons.Script.SConsOptions.SConsValues(
            parser.get_default_values()
        )
        parser.parse_args(args=[], values=values)
        SCons.Script.Main.OptionsParser = parser

        # -- Reset the scons target list variable.
        SCons.Node.FS.default_fs = None

        # -- Clear the SCons targets
        SCons.Environment.CleanTargets = {}

        # -- Reset the default scons env, if it exists.
        #
        # pylint: disable=protected-access
        SCons.Defaults._default_env = None
        # pylint: enable=protected-access

    @staticmethod
    def get_targets() -> Dict:
        """Get the scons {target -> dependencies} dictionary."""
        return SCons.Environment.CleanTargets


def _make_test_scons_env(
    args: Dict[str, str] = None, extra_args: Dict[str, str] = None
) -> SConsEnvironment:
    """Creates a fresh apio scons env with given args. The env is created
    with a reference to the current directory.
    """

    # -- Bring scons to a starting state.
    SconsHacks.reset_scons_state()

    # -- Default, when we don't really care about the content.
    if args is None:
        args = {
            "platform_id": "darwin_arm64",
        }

    # -- If specified, overite/add extra args.
    if extra_args:
        args.update(extra_args)

    # -- Use the apio's scons env creation function.
    env = create_construction_env(args)

    return env


def test_dependencies(apio_runner: ApioRunner):
    """Test the verilog scanner which scans a verilog file and extract
    reference of files it uses.
    """

    with apio_runner.in_sandbox() as sb:

        # -- Write a test file name in the current directory.
        sb.write_file("test_file.v", DEPENDECIES_TEST_TEXT)

        # -- Create a scanner
        env = _make_test_scons_env()
        scanner = make_verilog_src_scanner(env)

        # -- Run the scanner. It returns a list of File.
        file = FS.File(FS(), "test_file.v")
        dependency_files = scanner.function(file, env, None)

        # -- Create a list with file name strings.
        file_names = []
        for f in dependency_files:
            assert isinstance(f, File)
            file_names.append(f.name)

        # -- Check the list. The scanner returns the files sorted and
        # -- with dulicates removed.
        assert file_names == ["apio_testing.vh", "v771499.list"]


def test_has_testbench_name():
    """Tests the scons_util.test_is_testbench() function"""

    env = _make_test_scons_env

    # -- Testbench names
    assert has_testbench_name(env, "aaa_tb.v")
    assert has_testbench_name(env, "aaa_tb.out")
    assert has_testbench_name(env, "bbb/aaa_tb.v")
    assert has_testbench_name(env, "bbb\\aaa_tb.v")
    assert has_testbench_name(env, "aaa__tb.v")
    assert has_testbench_name(env, "Aaa__Tb.v")
    assert has_testbench_name(env, "bbb/aaa_tb.v")
    assert has_testbench_name(env, "bbb\\aaa_tb.v")

    # -- Non testbench names.
    assert not has_testbench_name(env, "aaatb.v")
    assert not has_testbench_name(env, "aaa.v")


def test_is_verilog_src():
    """Tests the scons_util.is_verilog_src() function"""

    env = _make_test_scons_env()

    # -- Verilog source names
    assert is_verilog_src(env, "aaa.v")
    assert is_verilog_src(env, "bbb/aaa.v")
    assert is_verilog_src(env, "bbb\\aaa.v")
    assert is_verilog_src(env, "aaatb.v")
    assert is_verilog_src(env, "aaa_tb.v")

    # -- Non verilog source names.
    assert not is_verilog_src(env, "aaatb.vv")
    assert not is_verilog_src(env, "aaatb.V")
    assert not is_verilog_src(env, "aaa_tb.vh")


def test_env_args():
    """Tests the scons env args retrieval."""

    args = {
        "platform_id": "my_platform",
        "AAA": "my_str",
        "BBB": "False",
        "CCC": "True",
    }

    env = _make_test_scons_env(args.copy())
    result_args = get_args(env)
    assert result_args == args

    # -- String args
    assert arg_str(env, "AAA", "") == "my_str"
    assert arg_str(env, "ZZZ", "") == ""
    assert arg_str(env, "ZZZ", "abc") == "abc"
    assert arg_str(env, "ZZZ", None) is None

    # -- Bool args
    assert not arg_bool(env, "BBB", None)
    assert arg_bool(env, "CCC", None)
    assert not arg_bool(env, "ZZZ", False)
    assert arg_bool(env, "ZZZ", True)
    assert arg_bool(env, "ZZZ", None) is None


def test_env_platform_id():
    """Tests the env handling of the paltform_id var."""

    # -- Test with a non windows platform id.
    env = _make_test_scons_env({"platform_id": "darwin_arm64"})
    assert not is_windows(env)

    # -- Test with a windows platform id.
    env = _make_test_scons_env({"platform_id": "windows_amd64"})
    assert is_windows(env)


def test_env_forcing_color():
    """Tests the color forcing functionality of the scons env."""

    # -- Color forcing turned on (apio writes to a terminal)
    env = _make_test_scons_env(
        {"force_colors": "True", "platform_id": "darwin_arm64"}
    )
    assert force_colors(env)

    # -- Color forcing turned off (apio process is pipped out)
    env = _make_test_scons_env(
        {"force_colors": "False", "platform_id": "darwin_arm64"}
    )
    assert not force_colors(env)


def test_set_up_cleanup_ok(apio_runner: ApioRunner):
    """Tests the success path of set_up_cleanup()."""

    with apio_runner.in_sandbox():

        # -- Create an env with 'clean' option set.
        env = _make_test_scons_env()
        SetOption("clean", True)

        # -- Create files that shouldn't be cleaned up.
        Path("my_source.v")
        Path("apio.ini")

        # -- Create files that should be cleaned up.
        Path("zadig.ini").touch()
        Path("_build").mkdir()
        Path("_build/aaa").touch()
        Path("_build/bbb").touch()

        # -- Run the cleanup setup. It's expected to add a single
        # -- target with the dependencies to clean up.
        assert len(SconsHacks.get_targets()) == 0
        set_up_cleanup(env)
        assert len(SconsHacks.get_targets()) == 1

        # -- Get the target and its dependencies
        items_list = list(SconsHacks.get_targets().items())
        target, dependencies = items_list[0]

        # -- Verify the tartget name, hard coded in set_up_cleanup()
        assert target.name == "cleanup-target"

        # -- Verif the dependencies. These are the files to delete.
        file_names = [x.name for x in dependencies]
        assert file_names == ["aaa", "bbb", "zadig.ini", "_build"]


def test_set_up_cleanup_errors():
    """Tests the error conditions of the set_up_cleanup() function."""

    env = _make_test_scons_env()

    # -- Try without the option 'clean'. It should fail.
    with pytest.raises(AssertionError) as e:
        set_up_cleanup(env)
    assert "Option 'clean' is missing" in str(e)

    # -- Try with the option 'clean'=false. It should fail.
    SetOption("clean", False)
    with pytest.raises(AssertionError) as e:
        set_up_cleanup(env)
    assert "Option 'clean' is missing" in str(e)


def test_map_params():
    """Test the map_params() function."""

    env = _make_test_scons_env()

    # -- Empty cases
    assert map_params(env, [], "x_{}_y") == ""
    assert map_params(env, ["", "   "], "x_{}_y") == ""

    # -- Non empty cases
    assert map_params(env, ["a"], "x_{}_y") == "x_a_y"
    assert map_params(env, [" a "], "x_{}_y") == "x_a_y"
    assert map_params(env, ["a", "a", "b"], "x_{}_y") == "x_a_y x_a_y x_b_y"


def test_log_functions(capsys: LogCaptureFixture):
    """Tests the fatal_error() function."""

    # -- Create the scons env.
    env = _make_test_scons_env()

    # -- Test msg()
    msg(env, "My msg")
    captured = capsys.readouterr()
    assert "My msg\n" == captured.out

    # -- Test info()
    info(env, "My info")
    captured = capsys.readouterr()
    assert "Info: My info\n" == captured.out

    # -- Test warning()
    warning(env, "My warning")
    captured = capsys.readouterr()
    assert "Warning: My warning\n" == captured.out

    # -- Test error()
    error(env, "My error")
    captured = capsys.readouterr()
    assert "Error: My error\n" == captured.out

    # -- Test fatal_error()
    with pytest.raises(SystemExit) as e:
        fatal_error(env, "My fatal error")
    assert e.value.code == 1
    captured = capsys.readouterr()
    assert "Error: My fatal error\n" == captured.out


def test_force_colors(capsys: LogCaptureFixture):
    """Tests that the "force_colors" controls text coloring."""
    # -- Creating an env without force_colors defaul to false.
    env = _make_test_scons_env()
    assert not force_colors(env)

    # -- Output a message and verify no ansi colors.
    capsys.readouterr()  # clear
    msg(env, "xyz", fg="red")
    captured = capsys.readouterr()
    assert captured.out == "xyz\n"

    # -- Output a message and verify no ansi colors.
    env = _make_test_scons_env(extra_args={"force_colors": "False"})
    assert not force_colors(env)

    # -- Output a message and verify text is not colored.
    capsys.readouterr()  # clear
    msg(env, "xyz", fg="red")
    captured = capsys.readouterr()
    assert captured.out == "xyz\n"

    # -- Creating an env without with force_colors = True
    env = _make_test_scons_env(extra_args={"force_colors": "True"})
    assert force_colors(env)

    # -- Output a message and verify text is colored.
    capsys.readouterr()  # clear
    msg(env, "xyz", fg="red")
    captured = capsys.readouterr()
    assert captured.out == "\x1b[31mxyz\x1b[0m\n"


def test_get_constraint_file(
    capsys: LogCaptureFixture, apio_runner: ApioRunner
):
    """Test the get_constraint_file() function."""

    with apio_runner.in_sandbox():

        env = _make_test_scons_env()

        # -- If not .pcf files, should assume main name + extension and
        # -- inform the user about it.
        capsys.readouterr()  # Reset capture
        result = get_constraint_file(env, ".pcf", "my_main")
        captured = capsys.readouterr()
        assert "assuming 'my_main.pcf'" in captured.out
        assert result == "my_main.pcf"

        # -- If a single .pcf file, return it.
        Path("pinout.pcf").touch()
        result = get_constraint_file(env, ".pcf", "my_main")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert result == "pinout.pcf"

        # -- If thre is more than one, exit with an error message.
        Path("other.pcf").touch()
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            result = get_constraint_file(env, ".pcf", "my_main")
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert "Error: Found multiple '*.pcf'" in captured.out


def test_get_programmer_cmd(capsys: LogCaptureFixture):
    """Tests the function get_programmer_cmd()."""

    # -- Without a "prog" arg, expected to return "". This is the case
    # -- when scons handles a command that doesn't use the programmer.
    env = _make_test_scons_env()
    assert get_programmer_cmd(env) == ""

    # -- If prog is specified, expected to return it.
    env = _make_test_scons_env(extra_args={"prog": "my_prog aa $SOURCE bb"})
    assert get_programmer_cmd(env) == "my_prog aa $SOURCE bb"

    # -- If prog string doesn't contains $SOURCE, expected to exit with an
    # -- error message.
    env = _make_test_scons_env(extra_args={"prog": "my_prog aa SOURCE bb"})
    with pytest.raises(SystemExit) as e:
        capsys.readouterr()  # Reset capturing.
        get_programmer_cmd(env)
    captured = capsys.readouterr()
    assert e.value.code == 1
    assert "does not contain the '$SOURCE'" in captured.out


def test_make_verilator_config_builder(apio_runner: ApioRunner):
    """Tests the make_verilator_config_builder() function."""

    with apio_runner.in_sandbox() as sb:

        # -- Create a test scons env.
        env = _make_test_scons_env()

        # -- Call the tested function to create a builder.
        builder = make_verilator_config_builder(env, "test-text")

        # -- Verify builder suffixes.
        assert builder.suffix == ".vlt"
        assert builder.src_suffix == []

        # -- Create a target that doesn't exist yet.
        assert not exists("hardware.vlt")
        target = FS.File(FS(), "hardware.vlt")

        # -- Invoke the builder's action to create the target.
        builder.action(target, [], env)
        assert isfile("hardware.vlt")

        # -- Verify that the file was created with the tiven text.
        text = sb.read_file("hardware.vlt")

        assert text == "test-text"


def test_get_source_files(apio_runner):
    """Tests the get_source_files() function."""

    with apio_runner.in_sandbox():

        # -- Create a test scons env.
        env = _make_test_scons_env()

        # -- Make files verilog src names (out of order)
        Path("bbb.v").touch()
        Path("aaa.v").touch()

        # -- Make files with testbench names (out of order)
        Path("ccc_tb.v").touch()
        Path("aaa_tb.v").touch()

        # -- Make files with non related names.
        Path("ddd.vh").touch()
        Path("eee.vlt").touch()
        Path("subdir").mkdir()
        Path("subdir/eee.v").touch()

        # -- Invoked the tested function.
        srcs, testbenches = get_source_files(env)

        # -- Verify results.
        assert srcs == ["aaa.v", "bbb.v"]
        assert testbenches == ["aaa_tb.v", "ccc_tb.v"]
