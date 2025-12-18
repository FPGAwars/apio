# Apio boards

---

## apio boards

The `apio boards` command lists the FPGA boards supported by Apio.

You can define custom boards by placing a `boards.jsonc` file with your
board definition in your project directory, which overrides Apio’s default `boards.jsonc`.

> The apio board definitions are included in the apio 'definition' package
> that is updated periodically. 

<h3>Examples</h3>

```
apio boards                   # List all boards.
apio boards -v                # List with extra columns.
apio boards | grep ecp5       # Filter boards results.
apio boards --docs            # Generate a report for Apio docs
```

<h3>Options</h3>

```
-v, --verbose           Show detailed output.
-d, --docs              Format for Apio Docs.
-p, --project-dir path  Set the root directory for the project.
-h, --help              Show this message and exit.
```
