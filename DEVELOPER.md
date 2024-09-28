# Apio Developers Hints

This file is not intended for APIO users.

## Pre commit tests
Before submitting a new commit, make sure to run successfuly the following command
in the root directory of the repository.:

```shell
make check
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

## Running apio in the Visual Studio Code debugger.

The ``apio`` repository contains at its root the file ``.vscode/launch.json`` with debug
target for most of the ``apio`` commands. Make sure to open the roo folder of the repository for VSC to recognize the targets file. To select the debug target, click on the debug icon on the left sidebar and this will display above a pull down menu with the available debug target and a start icon.

The debug target can be viewed here https://github.com/FPGAwars/apio/blob/develop/.vscode/launch.json


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
The command ``apio system -i`` (not released yet as of Sep 2024) shows the source directory of the apio package used. For example:

```
$ apio system -i
Platform: darwin_arm64
Package:  /Users/user/projects/apio_dev/repo/apio
```
