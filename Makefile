.PHONY: deps cenv env lint test presubmit publish_test publish install

# NOTE: Some targets have a shortcuts or alias names that are listed on the same line.
#       The are provided for convinience or for backward competibility. For example
#       'check-all' has the aliases 'check_all' and 'ca'.

# Install dependencies for apio development
#
# Usage:
#     make deps
deps:
	python -m pip install --upgrade pip
	pip install flit black flake8 pylint tox pytest semantic-version pyserial importlib-metadata
	

# Create the virtual-environment and update dependencies
# 
# Usage:
#     make cenv
cenv:  
	python3 -m venv venv
	python3 -m venv venv --upgrade

# Usage
#     make env
env:
	@echo "For entering the virtual-environment just type:"
	@echo ". venv/bin/activate"


# Lint only, no tests. 
#
# Usage:
#     make lint
#     make l
lint l:
	python -m tox -e lint


# Offline tests only, no lint, single python version, skipping online tests.
# This is a partial but fast test.
#
# Usage:
#     make test
#     make t
test t:	
	python -m tox --skip-missing-interpreters false -e py312 -- --offline


# Tests and lint, single python version, all tests including online..
# This is a thorough but slow test and sufficient for testign before 
# commiting changes run this before submitting code.
#
# Usage:
#     make check
#     make c
check c:	
	python -m tox --skip-missing-interpreters false -e lint,py312


# Tests and lint, multiple python versions.
# Should be be run automatically on github.
#
# Usage:
#     make check-all
#     make check_all   // deprecated, to be deleted.
#     make ca
check-all check_all ca:
	python -m tox --skip-missing-interpreters false


# Publish to testPypi
#
# Usage:
#     make publish-test
#     make publish_test  // deprecated, to be deleted. 
publish-test publish_test:
	flit publish --repository testpypi


# Publish to PyPi
#
# Usage:
#     make publish
publish:
	python -m flit publish

## Install the tool locally
#
# Usage:
#     make instll
install:
	flit build
	flit install
