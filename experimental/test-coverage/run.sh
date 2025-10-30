#!/bin/bash -x

# pip install --upgrade pytest==8.4.2 pytest-cov==7.0.0 coverage==7.11.0

rm -rf .coverage htmlcov 

pytest -vv -s --cov --cov-report=html:htmlcov test_foo.py

ls -al .coverage*

open htmlcov/foo_py.html

