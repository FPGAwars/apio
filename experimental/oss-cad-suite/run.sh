#!/bin/bash

set -e

function load() {
  tag="$1"

  echo
  echo 
  echo "--------- Loading oss-cad-suite ${tag}"
  echo

  compact="${tag//-/}"

  mkdir -p packages

  cd packages

  rm -f oss-cad-suite-${tag}.tgz
  rm -rf oss-cad-suite-${tag}

  wget \
    https://github.com/YosysHQ/oss-cad-suite-build/releases/download/${tag}/oss-cad-suite-darwin-arm64-${compact}.tgz \
    -O oss-cad-suite-${tag}.tgz \
    -q

  tar -xzf oss-cad-suite-${tag}.tgz
  mv oss-cad-suite oss-cad-suite-${tag}

  rm -f oss-cad-suite-${tag}.tgz

  cd ..

  head "packages/oss-cad-suite-${tag}/share/yosys/ecp5/cells_bb.v"
}

function report() {
  tag="$1"

  echo
  echo 
  echo "--------- Reporting oss-cad-suite ${tag}"
  echo

  #compact="${tag//-/}"

  file="packages/oss-cad-suite-${tag}/share/yosys/ecp5/cells_bb.v"

  echo "$file"
  echo
  head "$file"
}

load "2025-10-08"
load "2025-10-09"

#report "2025-10-08"
#report "2025-10-09"


#load "2025-09-23"

#load "2025-10-01"

#load "2025-10-05"
#load "2025-10-06"
#load "2025-10-07"
#load "2025-10-08"
#load "2025-10-09"
#load "2025-10-10"


#load "2025-10-10"
#load "2025-10-15"
#load "2025-10-20"
#load "2025-10-25"


#load "2025-11-01"
#load "2025-12-01"
#load "2026-01-01"
#load "2026-01-25"
