#!/bin/bash

# Run this script each time a .proto file in this directory
# is modified.

# Input:
#    *.proto   - proto messages definitions.
#
# Outputs:
#    *_pb2.py  - python binding.
#    *_pb2.pyi - symbols for visual studio code.



# Exit on any error.
set -e

# This should be the repo root.
echo "Current directory is $PWD"

# Install the proto compiler
echo "Installing the proto compiler"
pip install --quiet grpcio-tools==1.76.0

proto_dir="apio/common/proto"

tmp_file="$proto_dir/_tmp"

# Clean old output files.
rm -f $proto_dir/*_pb2.py
rm -f $proto_dir/*_pb2.pyi
rm -f $tmp_file

# Compile
echo "Compiling:"
for f in $proto_dir/*.proto; do
  echo "- $f"
  python -m grpc_tools.protoc \
    -I. \
    --python_out=.  \
    --pyi_out=. \
    $f
done

# Patch generated stubs to disable pylint checks
echo "Patching:"
for f in $proto_dir/*_pb2.py*; do
  echo "- $f"
  mv $f $tmp_file
  echo "# pylint: disable=all" > $f
  echo >> $f
  cat $tmp_file >> $f
  rm $tmp_file
done

# All done OK
echo "All done"
