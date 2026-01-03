#!/bin/bash

# Bash script to install and run the official Model Context Protocol (MCP) Inspector
# This tool provides a web-based interface to explore and test MCP servers.
# Requirements: Node.js (v18 or later) and npm must be installed on your system.

set -e  # Exit immediately if any command fails

echo "Installing the MCP Inspector globally via npm..."

# Install the inspector package globally
npm install -g @modelcontextprotocol/inspector

echo "Installation complete."

echo "Starting the MCP Inspector..."
echo "Once running, open your browser at http://localhost:6274 (or the displayed URL)."
echo "Connect to your MCP server (e.g., http://localhost:8000/mcp) using Streamable HTTP transport."

# Run the inspector
mcp-inspector

# Note: The command is typically 'mcp-inspector' after global installation.
# If the command name differs in future versions, check with 'npm list -g @modelcontextprotocol/inspector'.
