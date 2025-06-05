#!/usr/bin/env bash 

# Run to update BOARDS.md with the latest apio boards info.

output="BOARDS.md"

rm -f $output

echo "Generating $output ..."

python scripts/generate_boards_doc.py > $output

echo "$output updated"
