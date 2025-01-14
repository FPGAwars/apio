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

    # -- Test if the project has testbenches.
    set +e
    ls *_tb.v
    TB_STATUS=$?
    set -e


    # -- Exceute apio commands in the project. They should succeeed.
    set -x
      apio clean
      apio build
      apio lint
      if [ $TB_STATUS -eq 0 ]; then
        apio test
      fi   
      apio graph
      apio report
      apio clean
    set +x

    # -- Go back to the repo's root.
    popd
    
done


