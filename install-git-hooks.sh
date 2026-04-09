#!/bin/sh
# Install git hooks for Claude Code solo dev
# This script configures git to use githooks/ directory

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOKS_DIR="$SCRIPT_DIR/githooks"

# Check if githooks directory exists
if [ ! -d "$HOOKS_DIR" ]; then
    echo "ERROR: githooks/ directory not found at $HOOKS_DIR"
    exit 1
fi

# Set git core.hooksPath to use githooks/
git config core.hooksPath "$HOOKS_DIR"

echo "Git hooks installed from: $HOOKS_DIR"
echo "Current hooksPath: $(git config core.hooksPath)"
