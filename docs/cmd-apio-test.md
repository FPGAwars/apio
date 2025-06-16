# Apio test

The `apio test` command simulates one or more testbenches in the project.
It is intended for automated testing of your design. Testbenches should
have filenames ending in `_tb` (e.g., `my_module_tb.v`) and should use
the `$fatal` directive to indicate errors.

## EXAMPLES

```
apio test                 # Run all *_tb.v testbenches
apio test my_module_tb.v  # Run a single testbench
```

## OPTIONS

```
-e, --env name          Use a named environment from apio.ini
-p, --project-dir path  Specify the project root directory
-h, --help              Show help message and exit
```

## NOTES

- Avoid using the Verilog `$dumpfile()` function, as it may override
  the default name and location Apio assigns for the generated `.vcd` file.

- Testbench paths must be relative to the project directory,
  even when using the `--project-dir` option.

- See the Apio example `alhambra-ii/getting-started` for a testbench
  that demonstrates recommended practices.

- For graphical signal visualization, use the `apio sim` command instead.
