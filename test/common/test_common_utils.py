"""Test for common_utils.py."""

from pathlib import Path
from apio.common.common_util import sort_files, file_sort_key_func


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
