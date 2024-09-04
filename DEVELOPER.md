# APIO Developers Hints

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


## Running APIO in a debugger

Set the debugger to run the ``apio_run.py`` main with the regular ``apio`` arguments. Set the project directory ot the project file or use the ``--project_dir`` apio argument to point to the project directory.

Example of an equivalent manual command:
```
python apio_run.py build --project_dir ~/projects/fpga/repo/hdl
```

## Running APIO commands using a dev repo

One way is to link the pip package to the dev repository. Something along these lines. Adjust patches to match your system. The ``pip show`` command shows the directory where the stock pip package is installed.

NOTE: This make the command ``apio init --scons`` opsolete since the scons files can be edited in the dev repository.

```
pip install apio
pip show apio
cd /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages
mv apio apio.original
ln -s ~/projects/apio_dev/repo/apio
```


