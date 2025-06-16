# Apio sim

The `apio sim` command runs a simulation for the default or specified
testbench and displays the results in a GTKWave window. Testbench files
should end with `_tb`, such as `main_tb.v` or `main_tb.sv`. You can set
the default testbench using the `default-testbench` option in `apio.ini`.
If this option is not set and there's only one testbench in the project,
that file will be used.

## EXAMPLES

```
apio sim                   # Simulate the default testbench
apio sim my_module_tb.v    # Simulate the specified testbench
apio sim my_module_tb.sv   # Simulate the specified testbench
```

## OPTIONS

```
-f, --force             Force simulation
-e, --env name          Use a named environment from apio.ini
-p, --project-dir path  Specify the project root directory
-h, --help              Show help message and exit
```

#### NOTES

- Avoid using the Verilog `$dumpfile()` function, as it can override the default name and location Apio assigns for the `.vcd` file.

- Testbench paths must always be relative to the project directory, even when using `--project-dir`.

- The `apio sim` command defines the `INTERACTIVE_SIM` macro, which can be used in your testbench to distinguish it from `apio test`. For instance, you might suppress certain errors during interactive simulation to inspect signals in GTKWave.

- For a sample testbench that utilizes this macro, see the apio example `alhambra-ii/getting-started`.

- When configuring signals in GTKWave, save your setup so you don’t have to repeat it each time.

EXAMPLE SIMULATION RESULTS

![](assets/sim-gtkwave.png)
