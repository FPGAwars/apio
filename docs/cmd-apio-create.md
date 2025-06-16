# Creating a New Project

The `apio create` command initializes a new `apio.ini` file. Use it to
start a new Apio project.

This command only generates a new `apio.ini` file. To create a full,
  buildable project, use `apio examples` to fetch a template for your board.

## EXAMPLES

```
apio create --board alhambra-ii
apio create --board alhambra-ii --top-module MyModule
```

## OPTIONS

```
-b, --board BOARD        Specify the target board. [required]
-t, --top-module name    Set the top-level module name.
-p, --project-dir path   Specify the project root directory.
-h, --help               Show help message and exit.
```


