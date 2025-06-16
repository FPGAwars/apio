# Apio raw

The `apio raw` command bypasses Apio's usual workflow to run tools directly. It is intended for advanced users familiar with those tools.

> Before execution, Apio temporarily modifies environment variables like `$PATH`
> to make its packages accessible. Use the option `--verbose` to view these changes.

## EXAMPLES

```
apio raw    -- yosys --version      # Show Yosys version
apio raw -v -- yosys --version      # Verbose output
apio raw    -- yosys                # Start Yosys in interactive mode
apio raw    -- icepll -i 12 -o 30   # Calculate ICE PLL parameters
apio raw    -- which yosys          # Locate yosys in the path
apio raw -v                         # Show Apio environment settings
apio raw -h                         # Show help message
```

> Use the `--` marker to separate Apio's own options from those passed
> to the tool being run.

## OPTIONS

```
-v, --verbose  Show detailed output
-h, --help     Show help message and exit
```
