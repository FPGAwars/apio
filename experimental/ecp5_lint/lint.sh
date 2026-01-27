#!/bin/bash

# Example script for linting a yosys ecp5 project.
# Source the yosys environment before executing this script.

# Print commands
set -x

# Exit on first error.
set -e

# Location of the oss-cad-suite packgae.
OSS_CAD_SUITE="${VIRTUAL_ENV}"

echo "Running verilator"

#verilator_bin --lint-only --bbox-unsup --timing -Wno-TIMESCALEMOD -Wno-MULTITOP _fixed_new_cells_bb.v

verilator_bin --lint-only --bbox-unsup --timing -Wno-TIMESCALEMOD -Wno-MULTITOP old_cells_bb.v

echo "Exit code = $?"


exit 0

# Run the linter
verilator_bin \
  --lint-only \
  --bbox-unsup \
  --timing \
  --top-module main \
  -I"${OSS_CAD_SUITE}/share/yosys/ecp5" \
  "${OSS_CAD_SUITE}/share/yosys/ecp5/cells_bb.v" \
  main.v \
  pll.v

# Report linter exit code. Should be 0.
echo "Exit code: ${?}"

