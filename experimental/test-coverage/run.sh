#!/bin/bash -x

pytest -vv -s --cov --cov-report=html:htmlcov test_foo.py

ls -al .coverage*

open htmlcov/foo_py.html

