"""Test for common_utils.py."""

from pathlib import Path
from apio.common.common_util import sort_files, file_sort_compare_func


def test_file_sort_compare_func():
    """Test"""

    # -- Use a shortcut for the function name.
    f = file_sort_compare_func

    assert f("a", "a") == 0
    assert f("A", "a") == 0
    assert f("a", "A") == 0
    assert f("A", "A") == 0

    assert f("a", "b") == -1
    assert f("A", "b") == -1
    assert f("a", "B") == -1
    assert f("A", "B") == -1

    assert f("b", "a") == 1
    assert f("B", "a") == 1
    assert f("b", "A") == 1
    assert f("B", "A") == 1

    assert f("b", "a/a") == -1
    assert f("a/a", "b") == 1

    assert f("a/a", "a/b") == -1
    assert f("a/b", "a/ ") == 1

    assert f(Path("a"), Path("b")) == -1
    assert f(Path("b"), Path("A")) == 1
    assert f(Path("a"), Path("a")) == 0
    assert f(Path("B"), Path("a")) == 1


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
