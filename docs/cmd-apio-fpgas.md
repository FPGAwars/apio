# Apio fpgas

---

## apio fpgas

The `apio fpgas` command lists FPGAs supported by Apio.

You can define custom FPGAs by placing a `fpgas.jsonc` file in the project directory,
which overrides the default configuration, provided they are supported by the
underlying tools.

> The apio board definitions are included in the apio 'definition' package
> that is updated periodically.

<h3>Examples</h3>

```
apio fpgas                 # List all FPGAs.
apio fpgas -v              # List with extra columns.
apio fpgas | grep gowin    # Filter FPGA results.
apio boards --docs         # Generate a report for Apio docs
```

<h3>Options</h3>

```
-v, --verbose           Show detailed output
-d, --docs              Format for Apio Docs.
-p, --project-dir path  Specify the project root directory
-h, --help              Show help message and exit
```
