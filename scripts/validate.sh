#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

echo "Step 1: Running tests..."
./scripts/run_tests.sh

echo ""
echo "Step 2: Building Docker image..."
docker build -t modelops-lite:1.0 .

echo ""
echo "Validation completed successfully!"
