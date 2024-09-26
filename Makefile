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


# Lints the apio code base and tests.
lint:
	python -m tox -e lint


# Developers this target to test before submitting a commit.
# It performs lint and test and requires a single python interpreter.
check:	
	python -m tox --skip-missing-interpreters false -e py312


# Similar to 'check' but test with  multiple Python versions
# that need to be pre installed..
full_check:
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

