#!/bin/bash
# Start the OpenClaw MCP server
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_DIR"
PYTHON=/Users/steve/miniconda3/envs/agent_game/bin/python

echo "Starting OpenClaw MCP Server..."
exec $PYTHON -m openclaw.mcp_server
