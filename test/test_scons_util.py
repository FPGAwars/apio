"""
Tests of scons_util.py
"""

from test.conftest import ApioRunner
from SCons.Script import DefaultEnvironment
from SCons.Script.SConscript import SConsEnvironment
from SCons.Node.FS import FS, File
from apio.scons.scons_util import (
    make_verilog_src_scanner,
    has_testbench_name,
    is_verilog_src,
)

DEPENDECIES_TEST_TEXT = """
// Test file
parameter v771499 = "v771499.list"
`include "apio_testing.vh"
parameter v771499 = "v771499.list"
`include "apio_testing.v
"""


def test_dependencies(apio_runner: ApioRunner):
    """Test the verilog scanner which scans a verilog file and extract
    reference of files it uses.
    """

    with apio_runner.in_disposable_temp_dir():

        # -- Write a test file name in the current directory.
        with open("test_file.v", "w", encoding="utf-8") as f:
            f.write(DEPENDECIES_TEST_TEXT)

        # -- Create a scanner
        env: SConsEnvironment = DefaultEnvironment(ENV={}, tools=[])
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

    env: SConsEnvironment = DefaultEnvironment(ENV={}, tools=[])

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

    env: SConsEnvironment = DefaultEnvironment(ENV={}, tools=[])

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
