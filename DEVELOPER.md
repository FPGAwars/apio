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

While developement it's handy to run apio commands that will use the dev repo being worked on rather than the released apio version installed by pip. One way to achive that is to symlink the dev repo instead of the pip installed apio package as outlined below. 
Adjust the example as needed to match your system.

```
pip install apio
pip show apio
# Replace the path below with the 'Location' path provided by 'pip show apio'.
cd /Library/Frameworks/Python.framework/Versions/3.12/lib/python3.12/site-packages
mv apio apio.original
# Replace the path below with to the 'apio' directory in your apio dev directory.
ln -s ~/projects/apio_dev/repo/apio apio
```

With this symbolic link, the python, resources, and SConstruct files will be loaded
from the dev repo you are developing on. Note that binaries such as yosys are not 
part of the dev repository and will be loaded from ~/.apio. 

