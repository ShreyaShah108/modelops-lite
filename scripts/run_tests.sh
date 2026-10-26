#!/usr/bin/env bash

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

if [ ! -x ".venv/bin/python" ]; then
    echo "Error: virtual environment not found at .venv/"
    exit 1
fi

echo "Running ModelOps Lite tests..."
.venv/bin/python -m pytest -v

echo "All tests passed!"
