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

# Clean old output files.
rm -f apio_pb2.py
rm -f apio_pb2.pyi

# Generate new
python -m grpc_tools.protoc \
  -I. \
  --python_out=.  \
  --pyi_out=. apio.proto


