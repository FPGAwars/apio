#!/bin/bash

# Print commands
set -x

# Exit on first error.
set -e

echo "Running verilator"

verilator_bin --lint-only --bbox-unsup --timing -Wno-TIMESCALEMOD -Wno-MULTITOP _fixed_new_cells_bb.v

echo "Exit code = $?"


