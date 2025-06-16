# Building a Project

The `apio build` command compiles the project's source files and
generates a bitstream ready for upload to the FPGA.

## EXAMPLES

```
apio build                   # Typical Usage
apio build -e debug          # Use a specific environment from apio.ini
apio build -v                # Show all verbose output
apio build --verbose-synth   # Verbose synthesis info
apio build --verbose-pnr     # Verbose place and route info
```

## OPTIONS

```
-e, --env name            Use a named environment from apio.ini
-p, --project-dir path    Set the project's root directory
-v, --verbose             Show all verbose output
    --verbose-synth       Show verbose synthesis stage output
    --verbose-pnr         Show verbose place-and-route stage output
-h, --help                Show help message and exit
```

## NOTES

* Specify the top module using the `top-module` option in `apio.ini`.
* Testbench files (`*_tb.v` and `*_tb.sv`) are ignored during build.
* Running `apio build` before `apio upload` is usually unnecessary.
* Run `apio clean` before building to force a full rebuild.
