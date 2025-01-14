#!/bin/bash

# Exit on first error.
set -e

# Change to repo's dir.
cd ..

# Find all apio.ini in icestudio projects
projects=$(find test-examples | grep icestudio | grep apio.ini)

for proj in $projects;  do
    # Get the parent directory of apio.ini
    proj="$(dirname "$proj")"

    echo
    echo "--- PROJECT  $proj"
    echo

    # -- Go to the project's dir.
    pushd $proj

    # -- Exceute apio commands in the project. They should succeeed.
    set -x
      apio clean
      apio build
      # apio lint
      # apio test
      apio graph
      apio report
      apio clean
    set +x

    popd
    
done


