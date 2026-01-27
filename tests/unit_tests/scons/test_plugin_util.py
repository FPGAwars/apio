"""
Tests of the scons plugin_util.py functions.
"""

import re
import os
from os.path import isfile, exists, join
import pytest
from SCons.Node.FS import FS
from SCons.Action import FunctionAction
from pytest import LogCaptureFixture
from tests.unit_tests.scons.testing import make_test_apio_env
from tests.conftest import ApioRunner
from apio.common.apio_console import cunstyle
from apio.common import apio_console
from apio.common.proto.apio_pb2 import TargetParams, UploadParams, LintParams
from apio.scons.plugin_util import (
    get_constraint_file,
    verilog_src_scanner,
    get_programmer_cmd,
    map_params,
    make_verilator_config_builder,
    verilator_lint_action,
)


def test_get_constraint_file(
    apio_runner: ApioRunner, capsys: LogCaptureFixture
):
    """Test the get_constraint_file() method."""

    with apio_runner.in_sandbox() as sb:

        apio_env = make_test_apio_env()

        # -- If not .pcf files, should print an error and exit.
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            result = get_constraint_file(apio_env, ".pcf")
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert "No constraint file '*.pcf' found" in cunstyle(captured.out)

        # -- If a single .pcf file, return it. Constraint file can also be
        # -- in subdirectories as we test here
        file1 = os.path.join("lib", "pinout.pcf")
        sb.write_file(file1, "content1")
        result = get_constraint_file(apio_env, ".pcf")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert result == file1

        # -- If there is more than one, exit with an error message.
        file2 = "other.pcf"
        sb.write_file(file2, "content2")
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            result = get_constraint_file(apio_env, ".pcf")
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert "Error: Found 2 constraint files '*.pcf'" in cunstyle(
            captured.out
        )

        # -- If the user specified a valid file then return it, regardless
        # -- if it exists or not.
        apio_env.params.apio_env_params.constraint_file = "xyz.pcf"
        capsys.readouterr()  # Reset capture
        result = get_constraint_file(apio_env, ".pcf")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert result == "xyz.pcf"

        # -- File extension should match the architecture.
        apio_env.params.apio_env_params.constraint_file = "xyz.bad"
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            result = get_constraint_file(apio_env, ".pcf")
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert (
            "Constraint file should have the extension '.pcf': xyz.bad"
            in cunstyle(captured.out)
        )

        # -- Path under _build is not allowed.
        apio_env.params.apio_env_params.constraint_file = "_build/xyz.pcf"
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            result = get_constraint_file(apio_env, ".pcf")
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert (
            "Error: Constraint file should not be under _build: _build/xyz.pcf"
            in cunstyle(captured.out)
        )

        # -- Path should not contain '../
        apio_env.params.apio_env_params.constraint_file = "a/../xyz.pcf"
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            result = get_constraint_file(apio_env, ".pcf")
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert (
            "Error: Constraint file path should not contain '..': a/../xyz.pcf"
            in cunstyle(captured.out)
        )


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
        builder = make_verilator_config_builder(
            sb.packages_dir,
            rules_to_supress=[
                "SPECIFYIGN",
            ],
        )

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
        assert "lint_off -rule SPECIFYIGN" in text, text


def test_verilator_lint_action_min(apio_runner: ApioRunner):
    """Tests the verilator_lint_action() function with minimal params."""

    with apio_runner.in_sandbox():

        # -- Create apio scons env.
        apio_env = make_test_apio_env(
            targets=["lint"], target_params=TargetParams(lint=LintParams())
        )

        # -- Call the tested function with minimal args.
        action = verilator_lint_action(
            apio_env, extra_params=None, lib_dirs=None, lib_files=None
        )

        # -- The return action is a list of two steps, a function to call and
        # -- a string with a command.
        assert isinstance(action, list)
        assert len(action) == 2
        assert isinstance(action[0], FunctionAction)
        assert isinstance(action[1], str)

        # -- Collapse consecutive spaces in the string.
        normalized_cmd = re.sub(r"\s+", " ", action[1])

        # -- Verify the string
        assert (
            "verilator_bin --lint-only --quiet --bbox-unsup --timing "
            "-Wno-TIMESCALEMOD -Wno-MULTITOP -DAPIO_SIM=0 --top-module main "
            f"_build{os.sep}default{os.sep}hardware.vlt $SOURCES"
            == normalized_cmd
        )


def test_verilator_lint_action_max(apio_runner: ApioRunner):
    """Tests the verilator_lint_action() function with maximal params."""

    with apio_runner.in_sandbox():

        # -- Create apio scons env.
        apio_env = make_test_apio_env(
            targets=["lint"],
            target_params=TargetParams(
                lint=LintParams(
                    top_module="my_top_module",
                    verilator_all=True,
                    verilator_no_style=True,
                    verilator_no_warns=["aa", "bb"],
                    verilator_warns=["cc", "dd"],
                )
            ),
        )

        # -- Call the tested function with minimal args.
        action = verilator_lint_action(
            apio_env,
            extra_params=["param1", "param2"],
            lib_dirs=["dir1", "dir2"],
            lib_files=["file1", "file2"],
        )

        # -- The return action is a list of two steps, a function to call and
        # -- a string with a command.
        assert isinstance(action, list)
        assert len(action) == 2
        assert isinstance(action[0], FunctionAction)
        assert isinstance(action[1], str)

        # -- Collapse consecutive spaces in the string.
        normalized_cmd = re.sub(r"\s+", " ", action[1])
        # -- Verify the string
        assert (
            "verilator_bin --lint-only --quiet --bbox-unsup --timing "
            "-Wno-TIMESCALEMOD -Wno-MULTITOP -DAPIO_SIM=0 -Wall -Wno-style "
            "-Wno-aa -Wno-bb -Wwarn-cc -Wwarn-dd --top-module my_top_module "
            'param1 param2 -I"dir1" -I"dir2" '
            f"_build{os.sep}default{os.sep}hardware.vlt "
            '"file1" "file2" $SOURCES' == normalized_cmd
        )
