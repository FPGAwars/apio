# Apio examples

The `apio examples` command group includes subcommands for listing and
fetching example projects provided by Apio. Each example is a
self-contained project that can be built and uploaded to its respective FPGA board.

## EXAMPLES

```
-h, --help  Show this message and exit.
```

## SUBCOMMANDS

```
apio examples list
apio examples fetch
```

---

# Apio examples list

The `apio examples list` command shows available Apio project examples.

## EXAMPLES

```
apio examples list                     # List all examples
apio examples list  -v                 # Verbose output
apio examples list | grep alhambra-ii  # Filter for alhambra-ii examples
apio examples list | grep -i blink     # Filter for blinking examples
```

## OPTIONS

```
-v, --verbose  Show detailed output.
-h, --help     Show this message and exit.
```

---

# Apio examples fetch

The `apio examples fetch` command retrieves a single example or all examples
for a specific board. The default destination directory is the current directory and it can be overriden using the `--dst` flag. If the
destination directory already exists, it must be empty.

## EXAMPLES

```
apio examples fetch alhambra-ii/ledon    # Single example
apio examples fetch alhambra-ii          # All examples for the board
apio examples fetch alhambra-ii -d work  # Explicit destination
```

## OPTIONS

```
-d, --dst path  Set a different destination directory.
-h, --help      Show this message and exit.
```
