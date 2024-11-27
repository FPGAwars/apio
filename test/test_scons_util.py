"""
Tests of scons_util.py
"""

from typing import Dict
from test.conftest import ApioRunner
import pytest
from SCons.Script.SConscript import SConsEnvironment
from SCons.Node.FS import FS, File
from SCons.Defaults import DefaultEnvironment
import SCons.Defaults
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
    check_default_scons_env_not_used,
)

DEPENDECIES_TEST_TEXT = """
// Test file
parameter v771499 = "v771499.list"
`include "apio_testing.vh"
parameter v771499 = "v771499.list"
`include "apio_testing.v
"""


def _make_test_env(args: Dict[str, str] = None) -> SConsEnvironment:
    """Creates a fresh apio scons env with given args."""

    # -- Check that the default scons env was not used.
    check_default_scons_env_not_used()

    # -- Default, when we don't really care about the content.
    if args is None:
        args = {
            "platform_id": "darwin_arm64",
            "force_colors": "False",
        }

    # -- Use the apio specific env creation function.
    env = create_construction_env(args)

    # -- Check that the default scons env was not used.
    check_default_scons_env_not_used()

    return env


def test_dependencies(apio_runner: ApioRunner):
    """Test the verilog scanner which scans a verilog file and extract
    reference of files it uses.
    """

    with apio_runner.in_disposable_temp_dir():

        # -- Write a test file name in the current directory.
        with open("test_file.v", "w", encoding="utf-8") as f:
            f.write(DEPENDECIES_TEST_TEXT)

        # -- Create a scanner
        env = _make_test_env()
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

    env = _make_test_env

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

    env = _make_test_env()

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

    env = _make_test_env(args.copy())
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
    env = _make_test_env({"platform_id": "darwin_arm64"})
    assert not is_windows(env)

    # -- Test with a windows platform id.
    env = _make_test_env({"platform_id": "windows_amd64"})
    assert is_windows(env)


def test_env_forcing_color():
    """Tests the color forcing functionality of the scons env."""

    # -- Color forcing turned on (apio writes to a terminal)
    env = _make_test_env(
        {"force_colors": "True", "platform_id": "darwin_arm64"}
    )
    assert force_colors(env)

    # -- Color forcing turned off (apio process is pipped out)
    env = _make_test_env(
        {"force_colors": "False", "platform_id": "darwin_arm64"}
    )
    assert not force_colors(env)


def test_default_env_check():
    """Teest that check_default_scons_env_not_used() throws an assertion
    exception when the default scons env is used.
    """
    # -- Since _default_env is private we supress lint warning.
    # pylint: disable=protected-access

    # -- Should not throw an exception when _default_env is not None.
    assert SCons.Defaults._default_env is None
    check_default_scons_env_not_used()

    # -- Using the default enrivornment makes _default_env non None.
    DefaultEnvironment(ENV={}, tools=[])
    assert SCons.Defaults._default_env is not None

    # -- This checks that the function has a failing assertion.
    with pytest.raises(AssertionError):
        check_default_scons_env_not_used()

    # -- Restore _default_env to None, for any other test that may sill need
    # -- to run.
    SCons.Defaults._default_env = None

    # pylint: enable=protected-access
