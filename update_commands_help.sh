#!/bin/bash

# Run to update COMMAND_HELP.md with the latest apio commands help text.

output="COMMANDS_HELP.md"

rm -f $output

echo "Generating $output ..."

python scripts/generate_commands_help.py > $output

echo "$output updated"
