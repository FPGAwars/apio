"""Test foo.py"""

import os
import foo
from pathlib import Path


def test_foo():
    """Test the parent/child processes coverage."""
    rcfile = Path(__file__).parent / ".coveragerc"
    os.environ["COVERAGE_RCFILE"] = str(rcfile)

    foo.launch_child()
