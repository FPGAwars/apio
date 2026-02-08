#!/bin/bash 

# Exit on first error.
set -e

source "/Users/user/Downloads/oss-cad-suite-2026-01-24/environment"

function run_yosys() {
  echo
  echo "---- Yosys"
  echo

  rm -rf _build_yosys
  mkdir -p _build_yosys

  yosys \
      -p "synth_gowin -top main -json _build_yosys/hardware.json" \
      -q \
      -DSYNTHESIZE \
      -DWIDTH=32 \
      main.v
}


function run_nextpnr() {
  local seed="$1"

  echo
  echo "---- Nextpnr ${seed}"
  echo

  rm -rf _build_nextpnr
  mkdir -p _build_nextpnr

  nextpnr-himbaechel \
      --device GW2AR-LV18QN88C8/I7 \
      --json _build_yosys/hardware.json \
      --write _build_nextpnr/hardware.pnr.json \
      --report _build_nextpnr/hardware.pnr \
      --vopt family=GW2A-18C \
      --vopt cst=pinout.cst \
      -q \
      --seed ${seed}
}

run_yosys

seed=0

while true; do
    run_nextpnr "${seed}"
    ((seed++))
done


