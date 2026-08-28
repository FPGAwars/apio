#!/bin/bash

# Run this script each time apio.proto is modified.

# Input:
#    apio-definitions.proto   - proto messages definitions.
#
# Outputs:
#    apio_definitions_pb2.py  - python binding.
#    apio_definitions_pb2.pyi - symbols for visual studio code.



# Exit on any error.
set -e

# This is the proto compiler
echo "Installing the proto compiler"
pip install --quiet grpcio-tools==1.76.0

patch="
# pylint: disable=all
"

tmp_file="_tmp"

# Patch a generated python stub to have a pylint directive
# to supress warnings. Otherwise linting apio would result
# in many warnings we don't care about.
patch_proto () {
  f=$1
  echo "Patching $f"
  mv $1 $tmp_file
  echo "$patch" > $1
  cat $tmp_file >> $1
  rm $tmp_file
}

# Clean old output files.
rm -f *_pb2.py
rm -f $tmp_file

# Compile
echo "Compiling apio-common.proto"
python -m grpc_tools.protoc \
  -I. \
  --python_out=.  \
  --pyi_out=. \
  apio-common.proto

patch_proto apio_common_pb2.py
patch_proto apio_common_pb2.pyi

echo "Compiling apio-definitions.proto"
python -m grpc_tools.protoc \
  -I. \
  --python_out=.  \
  --pyi_out=. \
  apio-definitions.proto

patch_proto apio_definitions_pb2.py
patch_proto apio_definitions_pb2.pyi

# All done OK
echo "All done"
