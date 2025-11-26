#!/usr/bin/env python
"""
Generate docs/methodology/README.md from the contents of docs/methodology/.

Usage:
    python scripts/generate_methodology_index.py

This script:
- Scans docs/methodology/ for .md files (excluding README.md).
- Extracts the first heading (# or ##) to use as the link title.
- Writes an index with links to each file.

Intended to reduce manual maintenance of the methodology index and keep
navigation in sync with the actual files.
"""

from pathlib import Path
import re
from typing import List, Tuple


DOCS_DIR = Path("docs")
METHODOLOGY_DIR = DOCS_DIR / "methodology"
OUTPUT_FILE = METHODOLOGY_DIR / "README.md"


def find_markdown_files(root: Path) -> List[Path]:
    """Return a list of markdown files under root, excluding README.md."""
    files: List[Path] = []
    for path in sorted(root.glob("*.md")):
        if path.name.lower() == "readme.md":
            continue
        files.append(path)
    return files


def extract_title(md_path: Path) -> str:
    """
    Extract the first level-1 or level-2 heading from a markdown file.
    If none is found, derive a title from the filename.
    """
    heading_pattern = re.compile(r"^(#{1,2})\s+(.*)$")

    try:
        text = md_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return md_path.stem.replace("_", " ").title()

    for line in text.splitlines():
        match = heading_pattern.match(line.strip())
        if match:
            # Return the heading text without trailing hashes
            title = match.group(2).strip().rstrip("#").strip()
            return title

    # Fallback: filename-based title
    return md_path.stem.replace("_", " ").title()


def build_entries() -> List[Tuple[str, str]]:
    """
    Build a list of (relative_path, title) tuples for methodology markdown files.
    Paths are relative to docs/ for MkDocs-friendly linking.
    """
    entries: List[Tuple[str, str]] = []

    md_files = find_markdown_files(METHODOLOGY_DIR)
    for path in md_files:
        # Path relative to docs/ (so 'methodology/xyz.md')
        rel_path = path.relative_to(DOCS_DIR).as_posix()
        title = extract_title(path)
        entries.append((rel_path, title))

    # Sort by filename path for stable ordering
    entries.sort(key=lambda t: t[0])
    return entries


def generate_index_markdown(entries: List[Tuple[str, str]]) -> str:
    """Generate the markdown content for the methodology index."""
    lines: List[str] = []

    lines.append("# Methodology Documentation Index\n")
    lines.append(
        "This page is automatically generated from the contents of the "
        "`docs/methodology/` folder.\n"
    )
    lines.append("The files are listed in alphabetical order by filename.\n")

    if not entries:
        lines.append("\n_No methodology documents found._\n")
        return "\n".join(lines)

    lines.append("\n## Sections\n")

    for rel_path, title in entries:
        # For display, drop the 'methodology/' prefix
        display_path = rel_path.replace("methodology/", "")
        lines.append(f"- **[{title}]({rel_path})**  ")
        lines.append(f"  (`{display_path}`)\n")

    return "\n".join(lines) + "\n"


def main() -> None:
    if not METHODOLOGY_DIR.exists():
        raise SystemExit(f"Directory not found: {METHODOLOGY_DIR}")

    entries = build_entries()
    content = generate_index_markdown(entries)
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"Wrote methodology index to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
