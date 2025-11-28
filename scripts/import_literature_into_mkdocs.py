#!/usr/bin/env python
"""
Sync literature notes into the MkDocs docs/ tree.

Usage:
    python scripts/import_literature_into_mkdocs.py

What it does:
- Ensures `docs/literature/reading-plan/` and `docs/literature/summaries/` exist.
- Copies all *.md files from:
    - literature/reading-plan/ -> docs/literature/reading-plan/
    - literature/summaries/    -> docs/literature/summaries/
- Creates/updates docs/literature/index.md with links.

Run this before `mkdocs build` or `mkdocs serve`, or hook it into a
gen-files pipeline if you’re using MkDocs plugins.
"""

import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
LIT_ROOT = REPO_ROOT / "literature"
DOCS_ROOT = REPO_ROOT / "docs"

def copy_tree(src: Path, dst: Path) -> None:
    dst.mkdir(parents=True, exist_ok=True)
    if not src.exists():
        return
    for path in src.glob("*.md"):
        target = dst / path.name
        shutil.copy2(path, target)

def build_index(reading_plan_dst: Path, summaries_dst: Path, index_path: Path) -> None:
    lines = []
    lines.append("# Literature\n")
    lines.append("")
    lines.append("This section collects the long-term reading plan and paper summaries")
    lines.append("that support the CT phenotyping project and PhD preparation.\n")
    lines.append("")
    lines.append("## 1. Reading Plan\n")
    lines.append("")
    if reading_plan_dst.exists():
        for path in sorted(reading_plan_dst.glob("*.md")):
            rel = path.name
            title = path.stem.replace("_", " ")
            lines.append(f"- [{title}](reading-plan/{rel})")
    else:
        lines.append("_No reading plan files found yet._")
    lines.append("")
    lines.append("## 2. Paper Summaries\n")
    lines.append("")
    if summaries_dst.exists():
        for path in sorted(summaries_dst.glob("*.md")):
            if path.name.lower().startswith("template_"):
                continue
            title = path.stem.replace("_", " ")
            lines.append(f"- [{title}](summaries/{path.name})")
    else:
        lines.append("_No summaries have been synced yet._")
    lines.append("")
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text("\n".join(lines), encoding="utf-8")

def main() -> None:
    src_reading = LIT_ROOT / "reading-plan"
    src_summaries = LIT_ROOT / "summaries"

    dst_reading = DOCS_ROOT / "literature" / "reading-plan"
    dst_summaries = DOCS_ROOT / "literature" / "summaries"
    index_path = DOCS_ROOT / "literature" / "index.md"

    copy_tree(src_reading, dst_reading)
    copy_tree(src_summaries, dst_summaries)
    build_index(dst_reading, dst_summaries, index_path)

    print("Synced literature into docs/ and updated docs/literature/index.md")

if __name__ == "__main__":
    main()
