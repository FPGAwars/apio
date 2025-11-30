#!/usr/bin/env bash 

# The python script below requires apio to be installed as a python package.
invoke install-apio

# Run to update COMMANDS.txt with the latest apio commands help text.

output="COMMANDS.txt"

rm -f $output

echo "Generating $output ..."

python ./scripts/generate_commands_help.py > $output

echo "$output updated"
