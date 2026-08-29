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

# This is the proto compiler
echo "Installing the proto compiler"
pip install --quiet grpcio-tools==1.76.0

tmp_file="_tmp"

# Clean old output files.
rm -f *_pb2.py
rm -f *_pb2.pyi
rm -f $tmp_file

# Compile
for f in *.proto; do
  echo "- Compilling $f"
  python -m grpc_tools.protoc \
    -I. \
    --python_out=.  \
    --pyi_out=. \
    $f
done

# Patch generated stubs to disable pylint checks
for f in *_pb2.py *_pb2.pyi; do
  echo "- Patching   $f"
  mv $f $tmp_file
  echo "# pylint: disable=all" > $f
  echo >> $f
  cat $tmp_file >> $f
  rm $tmp_file
done

# All done OK
echo "All done"
