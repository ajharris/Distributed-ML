#!/usr/bin/env bash
set -euo pipefail

ISSUES_DIR="literature/issues"
LABEL="reading"   # change or remove this if you want no label

# Optional: set repo explicitly (otherwise gh uses current directory's repo)
# REPO="your-github-username/Distributed-ML"

for f in "$ISSUES_DIR"/*.md; do
  echo "Processing $f"

  # Extract the first line as the title, strip leading '# ' if present
  title=$(head -n 1 "$f" | sed 's/^# *//')

  # If title is empty, fall back to filename
  if [ -z "$title" ]; then
    title=$(basename "$f" .md)
  fi

  echo "Creating issue: $title"

  # Dry run: uncomment this first to see what would happen
  # echo gh issue create --title "$title" --body-file "$f" --label "$LABEL"
  # continue

  # Real run:
  gh issue create \
    --title "$title" \
    --body-file "$f" \
    --label "$LABEL"
    # If you set REPO above, add:  --repo "$REPO"

done

echo "Done creating issues."
