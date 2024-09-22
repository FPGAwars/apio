# Apio Developers Hints

This file is not intended for APIO users.

## Pre commit tests
Before submitting a new commit, make sure the following commands runs successfuly (in the repository root):

```shell
make lint
make tox
```

## Running an individual APIO test

Run from the repo root. Replace with the path to the desire test. Running ``pytest`` alone runs all the tests.

```shell
pytest test/code_commands/test_build.py
```


## Running apio in a debugger

Set the debugger to run the ``apio_run.py`` main with the regular ``apio`` arguments. Set the project directory ot the project file or use the ``--project_dir`` apio argument to point to the project directory.

Example of an equivalent manual command:
```
python apio_run.py build --project_dir ~/projects/fpga/repo/hdl
```

## Using the dev repository for apio commands.

You can tell pip to youse your apio dev repository for apio commands instead of the standard apio release. This allows quick edit/test cycles where you the modify code in your apio dev repository and  immediately test it by running ``apio`` commands in the console..

To use the local repo run this in the repo's root directory:
```
pip uninstall apio
pip install -e .
```

To return back to the release package run this (in any directory):
```
pip uninstall apio
pip install apio
```
