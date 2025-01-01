"""
Tests of the scons plug_util.py functions.
"""

from test.scons.test_apio_env import make_test_apio_env
from test.conftest import ApioRunner
import pytest
from SCons.Node.FS import FS
from pytest import LogCaptureFixture
from apio.scons.plugin_util import get_constraint_file, verilog_src_scanner


def test_get_constraint_file(
    capsys: LogCaptureFixture, apio_runner: ApioRunner
):
    """Test the get_constraint_file() method."""

    with apio_runner.in_sandbox() as sb:

        apio_env = make_test_apio_env()

        # -- If not .pcf files, should assume main name + extension and
        # -- inform the user about it.
        capsys.readouterr()  # Reset capture
        result = get_constraint_file(apio_env, ".pcf", "my_main")
        captured = capsys.readouterr()
        assert "assuming 'my_main.pcf'" in captured.out
        assert result == "my_main.pcf"

        # -- If a single .pcf file, return it.
        sb.write_file("pinout.pcf", "content")
        result = get_constraint_file(apio_env, ".pcf", "my_main")
        captured = capsys.readouterr()
        assert captured.out == ""
        assert result == "pinout.pcf"

        # -- If thre is more than one, exit with an error message.
        sb.write_file("other.pcf", "content")
        capsys.readouterr()  # Reset capture
        with pytest.raises(SystemExit) as e:
            result = get_constraint_file(apio_env, ".pcf", "my_main")
        captured = capsys.readouterr()
        assert e.value.code == 1
        assert "Error: Found multiple '*.pcf'" in captured.out


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
            "boards.json",
            "programmers.json",
            "fpgas.json",
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

        # -- Check the dependnecies
        file_names = [f.name for f in dependency_files]
        assert file_names == sorted(core_dependencies + file_dependencies)
