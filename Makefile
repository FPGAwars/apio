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

# Keep this list the same as in tox.ini.
lint_dirs = apio test test-boards

lint:  ## Lint the apio app code
	python -m black  $(lint_dirs)
	python -m flake8 $(lint_dirs)
	python -m pylint $(lint_dirs)
	
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
