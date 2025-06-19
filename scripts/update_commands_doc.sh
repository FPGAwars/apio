#!/usr/bin/env bash 

# Run to update COMMANDS.txt with the latest apio commands help text.

output="COMMANDS.txt"

rm -f $output

echo "Generating $output ..."

python ./generate_commands_help.py > $output

echo "$output updated"
