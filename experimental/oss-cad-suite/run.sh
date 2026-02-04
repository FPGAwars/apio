#!/bin/bash

set -e

function load() {
  tag="$1"

  echo
  echo 
  echo "--------- Loading oss-cad-suite ${tag}"
  echo

  compact="${tag//-/}"

  PACKAGES="/Users/user/Downloads/oss-packages"

  mkdir -p ${PACKAGES}

  cd ${PACKAGES}

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

  head "${PACKAGES}/oss-cad-suite-${tag}/share/yosys/ecp5/cells_bb.v"
}

function report() {
  tag="$1"

  echo
  echo 
  echo "--------- Reporting oss-cad-suite ${tag}"
  echo

  #compact="${tag//-/}"

  file="${PACKAGES}/oss-cad-suite-${tag}/share/yosys/ecp5/cells_bb.v"

  echo "$file"
  echo
  head "$file"
}

load "2025-10-08"
load "2026-02-02"

# report "2025-10-08"
# report "2026-02-02"

