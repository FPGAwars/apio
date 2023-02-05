.PHONY: deps cenv env lint tox publish publish_test

deps:  ## Install dependencies for apio development
	python -m pip install --upgrade pip
	pip install flit black flake8 pylint tox pytest
	

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
	

tox:   ## Run tox
	python -m tox

publish_test:  ## Publish to testPypi
	flit publish --repository pypitest

publish:  ## Publish to PyPi
	python -m flit publish

install:  ## Install the tool locally
	flit build
	flit install

tests: ## Make tests
	pytest apio test