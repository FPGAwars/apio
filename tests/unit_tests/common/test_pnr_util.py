"""Test for pnr_util.py."""

from apio.common.pnr_util import extract_clocks_from_pnr


def test_extract_clocks_from_pnr_normal():
    """A well-formed 'fmax' section maps to the {name: {fmax}} schema."""

    pnr_data = {
        "fmax": {
            "clk$glb_clk": {"achieved": 123.45},
            "clk2$glb_clk": {"achieved": 50.0},
        }
    }
    assert extract_clocks_from_pnr(pnr_data) == {
        "clk$glb_clk": {"fmax": 123.45},
        "clk2$glb_clk": {"fmax": 50.0},
    }


def test_extract_clocks_from_pnr_missing_fmax_key():
    """A report with no 'fmax' key at all returns {}, not None or KeyError."""

    assert extract_clocks_from_pnr({"utilization": {}}) == {}
    assert extract_clocks_from_pnr({}) == {}


def test_extract_clocks_from_pnr_empty_fmax():
    """An explicit empty 'fmax' dict returns {}."""

    assert extract_clocks_from_pnr({"fmax": {}}) == {}


def test_extract_clocks_from_pnr_non_dict_fmax():
    """A malformed, non-dict 'fmax' section (e.g. list or string) is
    skipped gracefully instead of raising AttributeError."""

    assert extract_clocks_from_pnr({"fmax": ["not", "a", "dict"]}) == {}
    assert extract_clocks_from_pnr({"fmax": "unexpected string"}) == {}
    assert extract_clocks_from_pnr({"fmax": None}) == {}


def test_extract_clocks_from_pnr_non_dict_clock_entry():
    """A malformed clock entry (not a dict) is skipped, while sibling
    well-formed entries are still extracted."""

    pnr_data = {
        "fmax": {
            "good_clk": {"achieved": 100.0},
            "bad_clk": "not-a-dict",
            "bad_clk2": None,
            "bad_clk3": 42,
        }
    }
    assert extract_clocks_from_pnr(pnr_data) == {
        "good_clk": {"fmax": 100.0},
    }


def test_extract_clocks_from_pnr_missing_achieved_key():
    """A clock entry with no 'achieved' key is skipped (achieved is None)."""

    pnr_data = {
        "fmax": {
            "clk_no_achieved": {"some_other_field": 1},
            "clk_ok": {"achieved": 10.0},
        }
    }
    assert extract_clocks_from_pnr(pnr_data) == {
        "clk_ok": {"fmax": 10.0},
    }


def test_extract_clocks_from_pnr_zero_achieved_is_kept():
    """An 'achieved' value of 0 is falsy but not None, and must still be
    included -- guards against a regression to a lazy truthy check."""

    pnr_data = {"fmax": {"clk_zero": {"achieved": 0}}}
    assert extract_clocks_from_pnr(pnr_data) == {
        "clk_zero": {"fmax": 0},
    }
