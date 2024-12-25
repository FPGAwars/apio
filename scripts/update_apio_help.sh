#!/bin/bash

# Run to update apio_help.md with the latest help text.

output="apio_help.md"

rm -f $output

echo "Collecting apio help..."

python collect_apio_help.py > $output

echo "Updated $output"
