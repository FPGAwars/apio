"""
Tests of the scons plugin_util.py functions.
"""

from os.path import isfile, exists
from test.scons.testing import make_test_apio_env, SconsHacks
from test.conftest import ApioRunner
from pathlib import Path
import pytest
from SCons.Node.FS import FS
from SCons.Script import SetOption
from pytest import LogCaptureFixture
from apio.common.apio_console import cunstyle
from apio.common.proto.apio_pb2 import TargetParams, UploadParams
from apio.scons.plugin_util import (
    get_constraint_file,
    verilog_src_scanner,
    is_verilog_src,
    has_testbench_name,
    source_files,
    get_programmer_cmd,
    map_params,
    make_verilator_config_builder,
    configure_cleanup,
)


def test_get_constraint_file(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Test the get_constraint_file() method."""

    with apio_runner.in_sandbox() as sb:

        apio_env = make_test_apio_env()

        # -- If not .pcf files, should assume main name + extension and
        # -- inform the user about it.
        capsys.readouterr()  # Reset capture
        result = get_constraint_file(apio_env, ".pcf", "my_main")
        captured = capsys.readouterr()
        assert "assuming 'my_main.pcf'" in cunstyle(captured.out)
        assert result == "my_main.pcf"

        # -- If a single .pcf file, return it.
        sb.write_file("pinout.pcf", "content")
        result = get_constraint_file(apio_env, ".pcf", "my_main")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert result == "pinout.pcf"

        # -- If there is more than one, exit with an error message.
        sb.write_file("other.pcf", "content")
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            result = get_constraint_file(apio_env, ".pcf", "my_main")
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert "Error: Found multiple '*.pcf'" in cunstyle(captured.out)


def test_verilog_src_scanner(apio_runner: ApioRunner):
    """Test the verilog scanner which scans a verilog file and extract
    reference of files it uses.
    """

    # -- Test file content with references. Contains duplicates and
    # -- references out of alphabetical order.
    file_content = """
        // Dummy file for testing.

        // Icestudio reference.
        parameter v771499 = "v771499.list"

        // System verilog include reference.
        `include "apio_testing.vh"

        // Duplicate icestudio reference.
        parameter v771499 = "v771499.list"

        // Verilog include reference.
        `include "apio_testing.v

        // $readmemh() function reference.
        $readmemh("my_data.hex", State_buff);
        """

    with apio_runner.in_sandbox() as sb:

        # -- Write a test file name in the current directory.
        sb.write_file("test_file.v", file_content)

        # -- Create a scanner
        apio_env = make_test_apio_env()
        scanner = verilog_src_scanner(apio_env)

        # -- Run the scanner. It returns a list of File.
        file = FS.File(FS(), "test_file.v")
        dependency_files = scanner.function(file, apio_env, None)

        # -- Files list should be empty since none of the dependency candidate
        # has a file.
        file_names = [f.name for f in dependency_files]
        assert file_names == []

        # -- Create file lists
        core_dependencies = [
            "apio.ini",
            "boards.jsonc",
            "programmers.jsonc",
            "fpgas.jsonc",
        ]

        file_dependencies = [
            "apio_testing.vh",
            "my_data.hex",
            "v771499.list",
        ]

        # -- Create dummy files. This should cause the dependencies to be
        # -- reported. (Candidate dependencies with no matching file are
        # -- filtered out)
        for f in core_dependencies + file_dependencies + ["non-related.txt"]:
            sb.write_file(f, "dummy-file")

        # -- Run the scanner again
        dependency_files = scanner.function(file, apio_env, None)

        # -- Check the dependencies
        file_names = [f.name for f in dependency_files]
        assert file_names == sorted(core_dependencies + file_dependencies)


def test_is_verilog_src():
    """Tests the is_verilog_src() function."""

    # -- Verilog and system-verilog source names,
    assert is_verilog_src("aaa.v")
    assert is_verilog_src("bbb/aaa.v")
    assert is_verilog_src("bbb\\aaa.v")
    assert is_verilog_src("aaatb.v")
    assert is_verilog_src("aaa_tb.v")
    assert is_verilog_src("aaa.sv")
    assert is_verilog_src("bbb\\aaa.sv")
    assert is_verilog_src("aaa_tb.sv")

    # -- Non verilog source names, system-verilog included.
    assert not is_verilog_src("aaatb.vv")
    assert not is_verilog_src("aaatb.V")
    assert not is_verilog_src("aaa_tb.vh")


def test_has_testbench_name():
    """Tests the test_is_testbench() function."""

    # -- Testbench names
    assert has_testbench_name("aaa_tb.v")
    assert has_testbench_name("aaa_tb.out")
    assert has_testbench_name("bbb/aaa_tb.v")
    assert has_testbench_name("bbb\\aaa_tb.v")
    assert has_testbench_name("aaa__tb.v")
    assert has_testbench_name("Aaa__Tb.v")
    assert has_testbench_name("bbb/aaa_tb.v")
    assert has_testbench_name("bbb\\aaa_tb.v")

    # -- Non testbench names.
    assert not has_testbench_name("aaatb.v")
    assert not has_testbench_name("aaa.v")


def test_get_source_files(apio_runner):
    """Tests the get_source_files() method."""

    with apio_runner.in_sandbox():

        apio_env = make_test_apio_env()

        # -- Make files verilog src names (out of order)
        Path("bbb.v").touch()
        Path("aaa.sv").touch()

        # -- Make files with testbench names (out of order)
        Path("ccc_tb.v").touch()
        Path("aaa_tb.sv").touch()

        # -- Make files with non related names.
        Path("ddd.vh").touch()
        Path("eee.vlt").touch()

        # -- Make files in subdirectories.
        Path("subdir1").mkdir()
        Path("subdir2").mkdir()
        Path("subdir1/eee.v").touch()
        Path("subdir2/eee_tb.v").touch()

        # -- Invoked the tested method.
        srcs, testbenches = source_files(apio_env)

        # -- Verify results.
        assert srcs == ["aaa.sv", "bbb.v", "subdir1/eee.v"]
        assert testbenches == ["aaa_tb.sv", "ccc_tb.v", "subdir2/eee_tb.v"]


def test_get_programmer_cmd(capsys: LogCaptureFixture):
    """Tests the function programmer_cmd()."""

    # -- Test a valid programmer command.
    apio_env = make_test_apio_env(
        targets=["upload"],
        target_params=TargetParams(
            upload=UploadParams(programmer_cmd="my_prog aa $SOURCE bb")
        ),
    )
    assert get_programmer_cmd(apio_env) == "my_prog aa $SOURCE bb"

    # -- If prog string doesn't contains $SOURCE, expected to exit with an
    # -- error message.
    apio_env = make_test_apio_env(
        targets=["upload"],
        target_params=TargetParams(
            upload=UploadParams(programmer_cmd="my_prog aa SOURCE bb")
        ),
    )
    with pytest.raises(SystemExit) as e:
        capsys.readouterr()  # Reset capturing.
        get_programmer_cmd(apio_env)
    captured = capsys.readouterr()
    assert e.value.code == 1
    assert "$SOURCE is missing" in captured.out


def test_map_params():
    """Test the map_params() function."""

    # -- Empty cases
    assert map_params([], "x_{}_y") == ""
    assert map_params(["", "   "], "x_{}_y") == ""

    # -- Non empty cases
    assert map_params(["a"], "x_{}_y") == "x_a_y"
    assert map_params([" a "], "x_{}_y") == "x_a_y"
    assert map_params(["a", "a", "b"], "x_{}_y") == "x_a_y x_a_y x_b_y"


def test_make_verilator_config_builder(apio_runner: ApioRunner):
    """Tests the make_verilator_config_builder() function."""

    with apio_runner.in_sandbox() as sb:

        # -- Create a test scons env.
        apio_env = make_test_apio_env()

        # -- Call the tested method to create a builder.
        builder = make_verilator_config_builder(sb.packages_dir)

        # -- Verify builder suffixes.
        assert builder.suffix == ".vlt"
        assert builder.src_suffix == []

        # -- Create a target that doesn't exist yet.
        assert not exists("hardware.vlt")
        target = FS.File(FS(), "hardware.vlt")

        # -- Invoke the builder's action to create the target.
        builder.action(target, [], apio_env.scons_env)
        assert isfile("hardware.vlt")

        # -- Verify that the file was created with the given text.
        text = sb.read_file("hardware.vlt")
        assert "verilator_config" in text, text
        assert "lint_off -rule COMBDLY" in text, text


def test_clean_if_requested(apio_runner: ApioRunner):
    """Tests the success path of set_up_cleanup()."""

    with apio_runner.in_sandbox():

        # -- Create an env with 'clean' option set.
        apio_env = make_test_apio_env()

        # -- Create files that shouldn't be cleaned up.
        Path("my_source.v").touch()
        Path("apio.ini").touch()

        # -- Create files that should be cleaned up.
        Path("zadig.ini").touch()
        Path("_build").mkdir()
        Path("_build/aaa").touch()
        Path("_build/bbb").touch()

        # -- Run clean_if_requested with no cleanup requested. It assert.
        assert len(SconsHacks.get_targets()) == 0
        with pytest.raises(AssertionError):
            configure_cleanup(apio_env)

        # -- Run the cleanup setup. It's expected to add a single
        # -- target with the dependencies to clean up.
        assert len(SconsHacks.get_targets()) == 0
        SetOption("clean", True)
        configure_cleanup(apio_env)
        assert len(SconsHacks.get_targets()) == 1

        # -- Get the target and its dependencies
        items_list = list(SconsHacks.get_targets().items())
        target, dependencies = items_list[0]

        # -- Verify the target name, hard coded in set_up_cleanup()
        assert target.name == "cleanup-target"

        # -- Verify the dependencies. These are the files to delete.
        file_names = [x.name for x in dependencies]
        assert file_names == ["aaa", "bbb", "zadig.ini", "_build"]
