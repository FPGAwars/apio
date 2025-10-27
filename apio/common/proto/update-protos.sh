#!/bin/bash

# Run this script each time apio.proto is modified.

# Input:
#    apio.proto   - proto messages definitions.
#
# Outputs:
#    apio_pb2.py  - python binding.
#    apio_pb2.pyi - symbols for visual studio code.
#
# Requiremenst:
#    pip install grpcio-tools

# Exit on any error.
set -e

patch="
# pylint: disable=C0114, C0115, C0301, C0411
# pylint: disable=E0245, E0602, E1139
# pylint: disable=R0913, R0801, R0917
# pylint: disable=W0223, W0613, W0622
"

tmp_file="_tmp"

patch_proto () {
  f=$1
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
python -m grpc_tools.protoc \
  -I. \
  --python_out=.  \
  --pyi_out=. apio.proto

# Inject the pylint directive to supress warnings.
patch_proto apio_pb2.py
patch_proto apio_pb2.pyi

# All done OK
echo "All done"





