# Contributing Apio examples

Apio examples are stored in the `examples` directory of the [FPGAwars/apio-examples](https://github.com/FPGAwars/apio-examples) repository and are distributed in the Apio `examples` package (type `apio examples list` to check its version).

To contribute a new example, submit a pull request to the [FPGAwars/apio-examples](https://github.com/FPGAwars/apio-examples) repository after confirming it meets the following requirements:

- The example includes an `info` file with a single-line description (max 50 characters).
- The example passes linting with no warnings and can be built and uploaded.
- The example path is `examples/<board-id>/<example-name>`, where `<board-id>` matches the value in `apio.ini` and `<example-name>` includes only lowercase letters (a–z), digits (0–9), and dashes (-), and begins with a letter.
- The example includes at least one testbench that passes `apio test` and `apio sim` without errors.
- Each testbench has a corresponding `.gtkw` file with a saved GTKWave state.

## NOTES

- Files may be placed in a single directory or organized into subdirectories.
- Verilog `.v` and SystemVerilog `.sv` files may be used in any combination.
- If `apio.ini` defines multiple environments, the rules above apply to each environment selected with the `--env` flag.
