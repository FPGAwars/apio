# NOTE: Some targets have a shortcuts or alias names that are listed on the same line.
#       The are provided for convenience or for backward compatibility. For example
#       'check-all' has the aliases 'check_all' and 'ca'.

# Install dependencies for apio development
#
# Usage:
#     make deps
#
.PHONY: deps
deps:
	python -m pip install --upgrade pip
	pip install flit black flake8 pylint tox pytest semantic-version pyserial importlib-metadata
	

# Create the virtual-environment and update dependencies
# 
# Usage:
#     make cenv
#
.PHONY: cenv
cenv:  
	python3 -m venv venv
	python3 -m venv venv --upgrade

# Usage
#     make env
#
.PHONY: env
env:
	@echo "For entering the virtual-environment just type:"
	@echo ". venv/bin/activate"


# Lint only, no tests. 
#
# Usage:
#     make lint
#     make l
#
.PHONY: lint l
lint l:
	python -m tox -e lint


# Offline tests only, no lint, single python version, skipping online tests.
# This is a partial but fast test.
#
# Usage:
#     make test
#     make t
#
.PHONY: test t
test t:	
	python -m tox --skip-missing-interpreters false -e py313 -- --offline

# Same as 'make test' above but with the oldest supported python version.
#
# Usage:
#     make test-oldest
#     make to
#
.PHONY: test-oldest to
test-oldest to:	
	python -m tox --skip-missing-interpreters false -e py39 -- --offline


# Tests and lint, single python version, all tests including online..
# This is a thorough but slow test and sufficient for testing before 
# committing changes run this before submitting code.
#
# Usage:
#     make check
#     make c
#
.PHONY: check c
check c:	
	python -m tox --skip-missing-interpreters false -e lint,py313


# Same as 'make check' above but with the oldest supported python version.
#
# Usage:
#     make check-oldest
#     make co
#
.PHONY: check-oldest co
check-oldest co:	
	python -m tox --skip-missing-interpreters false -e lint,py39


# Tests and lint, multiple python versions.
# Should be be run automatically on github.
#
# Usage:
#     make check-all
#     make check_all   // deprecated, to be deleted.
#     make ca
#
.PHONY: check-all check_all ca
check-all check_all ca:
	python -m tox --skip-missing-interpreters false


# Publish to testPypi
#
# Usage:
#     make publish-test
#     make publish_test  // deprecated, to be deleted.
#
.PHONY: publish-test publish_test
publish-test publish_test:
	flit publish --repository testpypi


# Publish to PyPi
#
# Usage:
#     make publish
#
.PHONY: publish
publish:
	python -m flit publish

## Install the tool locally
#
# Usage:
#     make install
#
.PHONY: install
install:
	flit build
	flit install
