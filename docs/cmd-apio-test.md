# Apio test

---

## apio test

The `apio test` command simulates one or more testbenches in the project.
It is intended for automated testing of your design. Testbenches should
have filenames ending in `_tb` (e.g., `my_module_tb.v`) and should use
the `$fatal` directive to indicate errors.

<h3>Examples</h3>

```
apio test                  # Run all *_tb.v and *_tb.sv testbenches.
apio test my_module_tb.v   # Run a single testbench.
apio test my_module_tb.sv  # Run a single System Verilog testbench.
apio test util/led_tb.v    # Run a testbench in a sub-folder.
apio test --default        # Run only the default testbench.
```

<h3>Options</h3>

```
-d, --default           Test only the default testbench
-e, --env name          Use a named environment from apio.ini
-p, --project-dir path  Specify the project root directory
-h, --help              Show help message and exit
```

<h3>Notes</h3>

- Do not use the Verilog `$dumpfile()` function, as it may override
  the default name and location Apio assigns for the generated `.vcd` file.

- The default testbench is the same that is used by the 'apio sim'
  command which is the one specified in `apio.ini` using the
  `default-testbench` option, or the only testbench, if the project
  contains exactly one testbnech.

- Testbench paths must be relative to the project directory,
  even when using the `--project-dir` option.

- See the Apio example `alhambra-ii/getting-started` for a testbench
  that demonstrates recommended practices.

- For graphical signal visualization, use the `apio sim` command instead.
