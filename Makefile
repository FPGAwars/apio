.PHONY: deps cenv env lint test presubmit publish_test publish install

# Install dependencies for apio development
deps:
	python -m pip install --upgrade pip
	pip install flit black flake8 pylint tox pytest semantic-version pyserial importlib-metadata
	

# Create the virtual-environment and update dependencies
cenv:  
	python3 -m venv venv
	python3 -m venv venv --upgrade


env:
	@echo "For entering the virtual-environment just type:"
	@echo ". venv/bin/activate"


# Lint only, no tests. 
lint:
	python -m tox -e lint


# Offline tests only, no lint, single python version, skipping online tests.
# This is a partial but fast test.
test:	
	python -m tox --skip-missing-interpreters false -e py312 -- --offline


# Tests and lint, single python version, all tests including online..
# This is a thorough but slow test and sufficient for testign before 
# commiting changes run this before submitting code.
 check:	
	python -m tox --skip-missing-interpreters false -e lint,py312


# Tests and lint, multiple python versions.
# Should be be run automatically on github.
check_all:
	python -m tox --skip-missing-interpreters false


# Publish to testPypi
publish_test:
	flit publish --repository testpypi


# Publish to PyPi
publish:
	python -m flit publish

## Install the tool locally
install:
	flit build
	flit install

