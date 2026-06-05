#!/bin/bash
# Build Docker images for OpenClaw tasks
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_DIR/docker"

echo "=== Building OpenClaw Docker Images ==="

echo ""
echo "[1/2] Building base image..."
docker build -t openclaw-base:latest -f "$DOCKER_DIR/Dockerfile.base" "$DOCKER_DIR"

echo ""
echo "[2/2] Building Core-01 image..."
docker build -t openclaw-core01:latest -f "$DOCKER_DIR/Dockerfile.core01" "$DOCKER_DIR"

echo ""
echo "=== Done! Images: ==="
docker images | grep openclaw
