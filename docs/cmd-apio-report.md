# Apio report

The `apio report` command provides resource utilization and timing
information for the design. It helps identify bottlenecks and verify
whether the design meets its target clock speed.

## EXAMPLES

```
apio report            # Show report
apio report --verbose  # Show detailed report
```

## OPTIONS

```
-e, --env name          Use a named environment from apio.ini
-p, --project-dir path  Specify the project root directory
-v, --verbose           Show detailed output
-h, --help              Show help message and exit
```

## EXAMPLE REPORT

```
FPGA Resource Utilization
┌────────────────┬────────┬──────────┬─────────┐
│  RESOURCE      │  USED  │   TOTAL  │  UTIL.  │
├────────────────┼────────┼──────────┼─────────┤
│  ICESTORM_LC   │    90  │    7680  │     1%  │
│  ICESTORM_PLL  │        │       2  │         │
│  ICESTORM_RAM  │        │      32  │         │
│  SB_GB         │     2  │       8  │    25%  │
│  SB_IO         │     9  │     256  │     3%  │
│  SB_WARMBOOT   │        │       1  │         │
└────────────────┴────────┴──────────┴─────────┘

Clock Information
┌─────────┬───────────────────┐
│  CLOCK  │  MAX SPEED [Mhz]  │
├─────────┼───────────────────┤
│  CLK    │           119.15  │
└─────────┴───────────────────┘
```
