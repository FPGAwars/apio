#!/usr/bin/env bash 

# Run to update COMMANDS.md with the latest apio commands help text.

output="COMMANDS.md"

rm -f $output

echo "Generating $output ..."

python scripts/generate_commands_help.py > $output

echo "$output updated"
