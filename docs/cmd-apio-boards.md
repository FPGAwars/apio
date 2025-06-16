# Listing FPGA Boards

The `apio boards` command lists the FPGA boards supported by Apio.

> You can define custom boards by placing a `boards.jsonc` file with your
> board definition in your project directory, which overrides Apio’s default `boards.jsonc`.

## EXAMPLES

```
apio boards                   # List all boards.
apio boards -v                # List with extra columns.
apio boards | grep ecp5       # Filter boards results.
```

## OPTIONS

```
-v, --verbose           Show detailed output.
-p, --project-dir path  Set the root directory for the project.
-h, --help              Show this message and exit.
```
