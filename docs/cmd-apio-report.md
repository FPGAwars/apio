# Apio report

---

## apio report

The `apio report` command provides resource utilization and timing
information for the design. It helps identify bottlenecks and verify
whether the design meets its target clock speed.

The `--verbose` option prints additional information such as as unused
resources and critical nets.

<h3>Examples</h3>

```
apio report            # Show report
apio report --verbose  # Show detailed report
```

<h3>Options</h3>

```
-e, --env name          Use a named environment from apio.ini
-p, --project-dir path  Specify the project root directory
-v, --verbose           Show detailed output
-h, --help              Show help message and exit
```

<h3>Example report</h3>

```
Used FPGA Resource
┌────────────────┬────────┬──────────┬─────────┐
│  RESOURCE      │  USED  │   TOTAL  │  USED%  │
├────────────────┼────────┼──────────┼─────────┤
│  ICESTORM_LC   │    90  │    7680  │     1%  │
│  SB_GB         │     2  │       8  │    25%  │
│  SB_IO         │     9  │     256  │     3%  │
└────────────────┴────────┴──────────┴─────────┘

Clock Information
┌─────────┬───────────────────┐
│  CLOCK  │  MAX SPEED [Mhz]  │
├─────────┼───────────────────┤
│  CLK    │           119.15  │
└─────────┴───────────────────┘
```
