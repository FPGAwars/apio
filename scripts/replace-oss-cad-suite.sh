#!/bin/bash -x

# A script to replace the install oss-cad-suite with one downloaded
# from yosys HQ. Note that loading a package directly from yosys
# is unsafe in general because it doesn't include possible modification
# that the Apio oss-cad-suite package builder may perform.
#
# To restore Apio's standard oss-cad-suite, run 'apio packages install -f'

# Exit on first error.
set -euo pipefail

# The yosys release tag to use.
YOSYS_TAG="2026-02-02"

# Temp working directory
TMP_DIR="/Users/user/Downloads"

# Apio's home directory
APIO_HOME="/Users/user/.apio"



# Create compacted Yosys date such as "20260202"
YOSYS_DATE="${YOSYS_TAG//-/}"

# Make sure apio and its packages are installed
apio packages install

# Get apio plagform-id
platform_id=$(apio api get-system | jq -r '.system."platform-id"')
echo "Apio platform-id: [${platform_id}]"

# Fail if empty or missing
if [ -z "$platform_id" ]; then
    echo "Error: Could not determine platform-id from 'apio api get-system'" >&2
    exit 1
fi

# Change to temp directory
cd ${TMP_DIR}
pwd

# Clean potential leftovers from previous runs
rm -f  oss-cad-suite-*.tgz
rm -rf oss-cad-suite

# Download the package
wget \
https://github.com/YosysHQ/oss-cad-suite-build/releases/download/${YOSYS_TAG}/oss-cad-suite-${platform_id}-${YOSYS_DATE}.tgz \
    -O oss-cad-suite-${YOSYS_DATE}.tgz

# Uncompress the package
tar -xzf oss-cad-suite-${YOSYS_DATE}.tgz

# Remove current installed Apio package
rm -rf ${APIO_HOME}/packages/oss-cad-suite

# Move the downloaded package to the apio dir.
# We move rather than copy to preserve symbolic links.
mv oss-cad-suite ${APIO_HOME}/packages/oss-cad-suite

# Test the installed package
source  ${APIO_HOME}/packages/oss-cad-suite/environment
yosys --version

echo "All done ok"


