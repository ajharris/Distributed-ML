#!/usr/bin/env bash
set -euo pipefail

# Name of the output ZIP
OUTPUT="tracked_files.zip"

# Ensure we are in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: This is not a git repository."
    exit 1
fi

# Remove existing zip to avoid merges
rm -f "$OUTPUT"

echo "Creating ZIP of all git-tracked files..."

# Use git ls-files to list only tracked files, then zip them
git ls-files -z | xargs -0 zip -9 "$OUTPUT"

echo "Done."
echo "Created: $OUTPUT"
