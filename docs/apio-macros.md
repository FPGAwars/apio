# Apio Macros

Apio handles Verilog marcros in two ways

1. User defined macros that are specified in the `apio.ini` project file using the
   [defines option](project-file.md#defines).

2. Automatic macros that are defined by the various apio commands as described
   below.

| Command               | \`APIO_SIM | \`SYNTHESIS |
| :-------------------- | :--------: | :---------: |
| `apio build`          |            |   defined   |
| `apio lint`           |     0      |   defined   |
| `apio lint --nosynth` |     0      |             |
| `apio graph`          |            |   defined   |
| `apio report`         |            |   defined   |
| `apio format`         |            |             |
| `apio test`           |     0      |             |
| `apio sim`            |     1      |             |

### APIO_SIM macro

This macro is intended for use in testbenches to distinguish between
`apio test`, where failing assertions abort the simulation, and
`apio sim`, where the simulation continues despite failing assertions and
generates a waveform file for inspection in GTKWave.

Sample assertion macoro:`

```
// This signals shows in gtkwave the location of the first error.
reg assertion_err = 0;

// A macro to assert that a signal value equals the expected value.
// The macro skip `$fatal` if running `apio sim` and does invoke it when
// running `apio test`.
`define EXPECT_EQ(actual, expected) \
  if ((actual) !== (expected)) begin \
    $display("ERROR at %s:%0d: expected %s = %0b but got %0b", \
             `__FILE__, `__LINE__, `"actual`", expected, actual); \
    assertion_err = 1; \
    if (!`APIO_SIM) $fatal; \
  end
```

### SYNTHESIS macro

This macro is intended for use in synthesizable modules that contain
functionality, such as primitive cells, that cannot be simulated. It allows
the module to provide an alternative implementation that is selected when
running a simulation.

```
`ifdef SYNTHESIS

  // Insert here implemenation for synthesis

`else

  // Insert here implemenation for simulation

`endif
```

### Other macros

Apio commands may define additional macros for compatibility with
underlying tools and libraries. These macros are not intended for
direct user use and may change in future versions.
