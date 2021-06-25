.PHONY: deps cenv env lint tox publish publish_test

deps:  ## Install dependencies
	python -m pip install --upgrade pip
	python -m pip install black flake8 flit pylint tox tox-gh-actions semantic_version polib
	python -m pip install pyjwt click pyserial requests

cenv:  ## Create the virtual-environment
	python3 -m venv venv

env:
	@echo "For entering the virtual-environment just type:"
	@echo ". venv/bin/activate"

lint:  ## Lint and static-check
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
	py.test apio test