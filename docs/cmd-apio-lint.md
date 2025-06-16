# Apio lint

The `apio lint` command checks the project's source files for errors, inconsistencies, and style violations using the `Verilator` tool included with Apio.

## EXAMPLES

```
apio lint                # Lint the entire design
apio lint -t my_module   # Lint only 'my_module' and its dependencies
apio lint --all          # Enable all warnings, including style warnings
```

## OPTIONS

```
--nostyle               Disable all style warnings
--nowarn nowarn         Disable specific warning(s)
--warn warn             Enable specific warning(s)
-a, --all               Enable all warnings, including code style warnings
-t, --top-module name   Restrict linting to this module and its dependencies
-e, --env name          Use a named environment from apio.ini
-p, --project-dir path  Specify the project root directory
-h, --help              Show help message and exit
```
