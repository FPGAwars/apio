.PHONY: deps cenv env lint tox publish publish_test

deps:  ## Install dependencies for apio development
	python -m pip install --upgrade pip
	pip install flit black flake8 pylint tox pytest semantic-version pyserial importlib-metadata
	

cenv:  ## Create the virtual-environment and update dependencies
	python3 -m venv venv
	python3 -m venv venv --upgrade

env:
	@echo "For entering the virtual-environment just type:"
	@echo ". venv/bin/activate"

lint:  ## Lint and static-check
	python -m black apio
	python -m flake8 apio
	python -m pylint apio
	
lint-test: ### Lint test scripts
	python -m pylint test/conftest.py
	python -m pylint test/test_apio.py
	python -m pylint test/code_commands/test_build.py

test-one:  ## Execute a test script
	pytest -v -s test/code_commands/test_build.py::test_build_complete1

tox:   ## Run tox
	python -m tox

publish_test:  ## Publish to testPypi
	flit publish --repository testpypi

publish:  ## Publish to PyPi
	python -m flit publish

install:  ## Install the tool locally
	flit build
	flit install

tests: ## Execute ALL the tests
	pytest apio test