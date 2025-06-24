"""Test for common_utils.py."""

from pathlib import Path
from os.path import join
from apio.common.common_util import (
    sort_files,
    file_sort_key_func,
    is_source_file,
    has_testbench_name,
    get_project_source_files,
)


def test_file_sort_compare_func():
    """Test"""

    # -- A shortcut to the tested key function.
    key = file_sort_key_func

    assert key("a") == key("a")
    assert key("A") == key("a")
    assert key("a") == key("A")
    assert key("A") == key("A")

    assert key("a") < key("b")
    assert key("A") < key("b")
    assert key("a") < key("B")
    assert key("A") < key("B")

    assert key("b") > key("a")
    assert key("B") > key("a")
    assert key("b") > key("A")
    assert key("B") > key("A")

    assert key("b") < key("a/a")
    assert key("a/a") > key("b")

    assert key("a/a") < key("a/b")
    assert key("a/b") > key("a/ ")

    assert key(Path("a")) < key(Path("b"))
    assert key(Path("b")) > key(Path("A"))
    assert key(Path("a")) == key(Path("a"))
    assert key(Path("B")) > key(Path("a"))


def test_sort_files():
    """Test the sort_files function."""

    assert sort_files([]) == []

    assert sort_files(
        [
            "a/a/c",
            "a/b/a",
            "a/a",
            "a/b",
            "a",
            "b",
            "c",
            "A/C",
            "B/D",
        ]
    ) == [
        "a",
        "b",
        "c",
        "a/a",
        "a/b",
        "A/C",
        "a/a/c",
        "a/b/a",
        "B/D",
    ]


def test_is_source_file():
    """Tests the is_source_file() function."""

    # -- Verilog and system-verilog source names,
    assert is_source_file("aaa.v")
    assert is_source_file("bbb/aaa.v")
    assert is_source_file("bbb\\aaa.v")
    assert is_source_file("aaatb.v")
    assert is_source_file("aaa_tb.v")
    assert is_source_file("aaa.sv")
    assert is_source_file("bbb\\aaa.sv")
    assert is_source_file("aaa_tb.sv")

    # -- Non verilog source names, system-verilog included.
    assert not is_source_file("aaatb.vv")
    assert not is_source_file("aaatb.V")
    assert not is_source_file("aaa_tb.vh")


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
        srcs, testbenches = get_project_source_files()

        # -- Verify results.
        assert srcs == ["aaa.sv", "bbb.v", join("subdir1", "eee.v")]
        assert testbenches == [
            "aaa_tb.sv",
            "ccc_tb.v",
            join("subdir2", "eee_tb.v"),
        ]
