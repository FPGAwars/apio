#!/bin/bash

# Run this script each time apio.proto is modified.

# Input:
#    apio.proto   - proto messages definitions.
#
# Outputs:
#    apio_pb2.py  - python binding.
#    apio_pb2.pyi - symbols for visual studio code.



# Exit on any error.
set -e

# This is the proto compiler
echo "Installing the proto compiler"
pip install --quiet grpcio-tools==1.76.0

patch="
# pylint: disable=all
"

tmp_file="_tmp"

patch_proto () {
  f=$1
  echo "Patching $f"
  mv $1 $tmp_file
  echo "$patch" > $1
  cat $tmp_file >> $1
  rm $tmp_file
}

# Clean old output files.
rm -f apio_pb2.py
rm -f apio_pb2.pyi
rm -f $tmp_file

# Generate new
echo "Compiling apio.proto"
python -m grpc_tools.protoc \
  -I. \
  --python_out=.  \
  --pyi_out=. apio.proto

# Inject the pylint directive to supress warnings.
patch_proto apio_pb2.py
patch_proto apio_pb2.pyi

# All done OK
echo "All done"
