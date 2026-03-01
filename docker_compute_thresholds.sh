#!/bin/bash

# ChainML Guard - Docker Helper Script
# Run Python scripts inside Docker container with all dependencies

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║              ChainML Guard - Docker Script Runner                        ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Error: Docker is not installed or not in PATH"
    exit 1
fi

echo "✓ Docker found"
echo ""

# Build the Docker image if needed
IMAGE_NAME="chainml-guard"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Building Docker image (this may take a minute on first run)..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker build -t "$IMAGE_NAME" . || {
    echo ""
    echo "❌ Error: Docker build failed"
    exit 1
}

echo ""
echo "✓ Docker image built successfully"
echo ""

# Run the threshold computation script
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Running threshold computation inside Docker container..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

docker run --rm \
    -v "$(pwd):/app" \
    -w /app \
    "$IMAGE_NAME" \
    python scripts/compute_thresholds.py

EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo "╔══════════════════════════════════════════════════════════════════════════╗"
    echo "║                         SUCCESS!                                         ║"
    echo "╚══════════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "✓ Threshold computation completed successfully"
    echo "✓ thresholds.json has been created in the project root"
    echo ""
    echo "Next steps:"
    echo "  1. Verify: cat thresholds.json"
    echo "  2. Run the Flask app in Docker:"
    echo "     docker run -p 5000:5000 -v \$(pwd):/app $IMAGE_NAME"
    echo "  3. Visit: http://localhost:5000"
    echo ""
else
    echo "❌ Error: Threshold computation failed (exit code: $EXIT_CODE)"
    echo "   Check the error messages above for details."
    exit $EXIT_CODE
fi
