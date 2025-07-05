#!/usr/local/bin/python

"""Diff two JSONC files, ignoring comments and key order."""

# pylint: disable=import-error

# Requires:
#   pip install deepdiff

import json
import sys
import re
from pathlib import Path
from deepdiff import DeepDiff


def remove_jsonc_comments(text):
    """Remove // and /* */ comments."""
    text = re.sub(r"//.*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    return text


def load_and_normalize_jsonc(path):
    """Load the jsonc file as a tree of dics."""
    raw = Path(path).read_text(encoding="utf-8")
    cleaned = remove_jsonc_comments(raw)
    data = json.loads(cleaned)
    return data


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python diff_jsonc.py file1.jsonc file2.jsonc")
        sys.exit(1)

    file1 = load_and_normalize_jsonc(sys.argv[1])
    file2 = load_and_normalize_jsonc(sys.argv[2])

    # print("---File 1 keys begin")
    # keys_list = file1.keys()
    # keys_list = sorted(keys_list)
    # for key in keys_list:
    #     print(key)
    # print("---File 1 keys end")

    diff = DeepDiff(file1, file2, ignore_order=True)
    if diff:
        print("Differences found:")
        print(diff.pretty())
    else:
        print("Files are equal (ignoring comments and key order).")
