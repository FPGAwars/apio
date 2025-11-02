#!/bin/bash -x

# Exit on errors
set -e

rm -rf .coverage _pytest-coverage

pip install -q "pytest>=8.4.2" "pytest-cov>=7.0.0"

pip install -q -e .

python -B -m pytest \
   -W error \
   -vv \
   --cov=apio \
   --cov=test \
   --cov-config=.coveragerc \
   --cov-append \
   --cov-report=html:_pytest-coverage \
   test/first_test.py \
   test/unit_tests \
   test/integration_tests

open _pytest-coverage/index.html












