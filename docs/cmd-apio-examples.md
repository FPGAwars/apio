# Apio examples

---

## apio examples

The `apio examples` command group includes subcommands for listing and
fetching example projects provided by Apio. Each example is a
self-contained project that can be built and uploaded to its respective FPGA board.

> The apio project examples are included in the apio 'examples' package
> which is updated periodically.

<h3>Examples</h3>

```
-h, --help  Show this message and exit.
```

<h3>Subcommands</h3>

```
apio examples list
apio examples fetch
```

---

## apio examples list

The `apio examples list` command shows available Apio project examples.

> The apio project examples are included in the apio 'examples' package
> which is updated periodically.

<h3>Examples</h3>

```
apio examples list                     # List all examples
apio examples list  -v                 # Verbose output
apio examples list | grep alhambra-ii  # Filter for alhambra-ii examples
apio examples list | grep -i blink     # Filter for blinking examples
apio examples list --docs              # Use Apio docs format.
```

<h3>Options</h3>

```
-v, --verbose  Show detailed output.
-d, --docs     Format for Apio Docs.
-h, --help     Show this message and exit.
```

---

## apio examples fetch

The `apio examples fetch` command retrieves a single example or all examples
for a specific board. The default destination directory is the current directory and it can be overriden using the `--dst` flag. If the
destination directory already exists, it must be empty.

> The apio project examples are included in the apio 'examples' package
> which is updated periodically.

<h3>Examples</h3>

```
apio examples fetch alhambra-ii/ledon    # Single example
apio examples fetch alhambra-ii          # All examples for the board
apio examples fetch alhambra-ii -d work  # Explicit destination
```

<h3>Options</h3>

```
-d, --dst path  Set a different destination directory.
-h, --help      Show this message and exit.
```
