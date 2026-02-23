#!/bin/bash

# Exit on first error.
set -e

rm -f _graph.dot
rm -f _graph.svg

python ./main.py

cat _graph.dot

apio raw -- dot -Tsvg _graph.dot -o _graph.svg

open _graph.svg


