.PHONY: deps cenv env lint test presubmit publish_test publish install

# TODO: Force specific packages versions to have consistency across deevelopment
# environments. Also make sure to sync with the versions in tox.ini
deps:  ## Install dependencies for apio development
	python -m pip install --upgrade pip
	pip install flit black flake8 pylint tox pytest semantic-version pyserial importlib-metadata
	

cenv:  ## Create the virtual-environment and update dependencies
	python3 -m venv venv
	python3 -m venv venv --upgrade

env:
	@echo "For entering the virtual-environment just type:"
	@echo ". venv/bin/activate"

lint:	## Run lint only
	python -m tox -e lint
	
test:	## Run tests only
	python -m tox --skip-env lint

presubmit: # Presubmit checks. Run full tox.
	python -m tox

publish_test:  ## Publish to testPypi
	flit publish --repository testpypi

publish:  ## Publish to PyPi
	python -m flit publish

install:  ## Install the tool locally
	flit build
	flit install

