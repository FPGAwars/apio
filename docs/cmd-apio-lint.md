# Apio lint

---

## apio lint

The `apio lint` command checks the project's source files for errors, inconsistencies, and style violations using the `Verilator` tool included with Apio.

If specified files are not specified, the top module of the project
and its dependencies are linted.


<h3>Examples</h3>

```
apio lint                # Lint the entire design
apio lint -t my_module   # Lint only 'my_module' and its dependencies
apio lint file1.v file2  # Lint specified files only
apio lint --all          # Enable all warnings, including style warnings
apio lint --nosynth      # Do not define the SYNTHESIS macro.
apio lint --novlt        # Disable the .vlt rule supression file.
```

By default, `apio lint` defines the `SYNTHESIS` macro to lint the
synthesizable portion of the design. To lint code that is hidden by
`SYNTHESIS`, use the `--nosynth option`.

To customize the behavior of the `verilator` linter, add the option
`verilator-extra-option` in the project file `apio.ini` with the extra
options you would like to use. 

<h3>Options</h3>

```
--nosynth               Do not define the SUNTHESIS macro.
--novlt                 Disable warning suppression .vlt file.
--nostyle               Disable all style warnings
--nowarn nowarn         Disable specific warning(s)
--warn warn             Enable specific warning(s)
-a, --all               Enable all warnings, including code style warnings
-t, --top-module name   Restrict linting to this module and its dependencies
-e, --env name          Use a named environment from apio.ini
-p, --project-dir path  Specify the project root directory
-h, --help              Show help message and exit
```
