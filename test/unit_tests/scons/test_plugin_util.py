"""
Tests of the scons plugin_util.py functions.
"""

from os.path import isfile, exists, join
from test.unit_tests.scons.testing import make_test_apio_env
from test.conftest import ApioRunner
import pytest
from SCons.Node.FS import FS
from pytest import LogCaptureFixture
from apio.common.apio_console import cunstyle
from apio.common import apio_console
from apio.common.proto.apio_pb2 import TargetParams, UploadParams
from apio.scons.plugin_util import (
    get_constraint_file,
    verilog_src_scanner,
    get_programmer_cmd,
    map_params,
    make_verilator_config_builder,
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
        $readmemh("subdir2/my_data.hex", State_buff);
        """

    with apio_runner.in_sandbox() as sb:

        # -- Write a test file name in the current directory.
        sb.write_file("subdir1/test_file.v", file_content)

        # -- Create a scanner
        apio_env = make_test_apio_env()
        scanner = verilog_src_scanner(apio_env)

        # -- Run the scanner. It returns a list of File.
        file = FS.File(FS(), "subdir1/test_file.v")
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
            join("subdir2", "my_data.hex"),
            join("subdir1", "v771499.list"),
        ]

        # -- Create dummy files. This should cause the dependencies to be
        # -- reported. (Candidate dependencies with no matching file are
        # -- filtered out)
        for f in core_dependencies + file_dependencies + ["non-related.txt"]:
            sb.write_file(f, "dummy-file")

        # -- Run the scanner again
        dependency_files = scanner.function(file, apio_env, None)

        # -- Check the dependencies
        file_names = [f.path for f in dependency_files]
        assert file_names == sorted(core_dependencies + file_dependencies)


def test_get_programmer_cmd():
    """Tests the function programmer_cmd()."""

    apio_console.configure()

    # -- Test a valid programmer command.
    apio_env = make_test_apio_env(
        targets=["upload"],
        target_params=TargetParams(
            upload=UploadParams(programmer_cmd="my_prog aa $SOURCE bb")
        ),
    )
    assert get_programmer_cmd(apio_env) == "my_prog aa $SOURCE bb"


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
