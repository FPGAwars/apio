#!/bin/bash

# Exit on first error.
set -e

rm -f modified-graph.*

python main.py

wc modified-graph.dot

apio raw -- dot -Tsvg modified-graph.dot -o modified-graph.svg

wc modified-graph.svg

#open modified-graph.svg

