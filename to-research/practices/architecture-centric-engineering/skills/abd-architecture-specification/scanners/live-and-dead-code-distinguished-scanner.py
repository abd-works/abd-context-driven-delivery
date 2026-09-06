#!/usr/bin/env python3
"""Flag folder entries in Source Layout that carry no live/dead/legacy tag.

The Source Layout section of a context file or the central spec contains a
folder tree. Every folder line MUST end with a bracketed tag:
  - a mechanism or package name tag  e.g.  [Partner Integrations]
  - [dead code]  or  [legacy]

A folder line with no tag reads as live architecture; if it is actually orphaned
the spec actively misleads engineers and AI assistants.

Heuristic: a "folder line" is any line that contains `+--` or `|   ` tree
decoration followed by a folder-like name (ending with `/` or matching a word
without an extension).  Plain file lines (containing `.ts`, `.js`, `.py`, etc.)
are skipped — the rule targets *folders*, not individual files.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List

_ROOT = Path(__file__).resolve().parent.parent
_REPO = _ROOT.parent.parent.parent.parent
for _p in (
    _REPO / "common" / "scripts",
    _ROOT / "scanners",
):
    s = str(_p)
    if s not in sys.path:
        sys.path.insert(0, s)

from scanner_runner import execute_scan_with_workspace  # noqa: E402
from scanner_bases import Scanner, Violation  # noqa: E402
from scanner_bases.resources.scan_context import FileScanContext  # noqa: E402
from arch_spec_context import build_arch_spec_context  # noqa: E402

# Lines that are part of a Source Layout tree
_TREE_LINE_RE = re.compile(r"[|+]\s*--\s+(\S+)")

# A tag looks like  [something]  anywhere on the line
_TAG_RE = re.compile(r"\[.+?\]")

# File extension patterns — skip plain file entries
_FILE_EXTENSION_RE = re.compile(r"\.\w{1,5}\b")

# Heading that introduces a source layout block
_SOURCE_LAYOUT_HEADING_RE = re.compile(
    r"^#{1,6}\s+(?:source\s+layout|source\s+tree|folder\s+structure|file\s+structure)\s*$",
    re.IGNORECASE | re.MULTILINE,
)

# End of a fenced code block
_CODE_FENCE_START = re.compile(r"^```")


def _source_layout_blocks(text: str) -> List[str]:
    """Return list of code-block contents that follow a Source Layout heading."""
    blocks: List[str] = []
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if _SOURCE_LAYOUT_HEADING_RE.match(line):
            # Look ahead for the next fenced code block
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith("```"):
                j += 1
            if j < len(lines) and lines[j].strip().startswith("```"):
                # Collect until closing fence
                j += 1
                block_lines: List[str] = []
                while j < len(lines) and not lines[j].strip().startswith("```"):
                    block_lines.append(lines[j])
                    j += 1
                blocks.append("\n".join(block_lines))
                i = j
                continue
        i += 1
    return blocks


class LiveAndDeadCodeDistinguishedScanner(Scanner):

    def scan_file_with_context(self, context: FileScanContext) -> List[dict]:
        if not context.exists:
            return []
        text = context.file_path.read_text(encoding="utf-8")
        blocks = _source_layout_blocks(text)
        if not blocks:
            return []

        violations: List[dict] = []
        for block in blocks:
            for lineno_offset, raw_line in enumerate(block.splitlines(), start=1):
                m = _TREE_LINE_RE.search(raw_line)
                if not m:
                    continue
                entry_name = m.group(1)
                # Skip individual file entries (e.g. composition.ts, index.js)
                if _FILE_EXTENSION_RE.search(entry_name):
                    continue
                if not _TAG_RE.search(raw_line):
                    violations.append(
                        Violation(
                            rule=self.rule,
                            violation_message=(
                                f"Folder '{entry_name.rstrip('/')}' in Source Layout has no tag. "
                                f"Add a mechanism/package name tag, [dead code], or [legacy] "
                                f"to indicate whether this folder is part of the running system."
                            ),
                            location=str(context.file_path),
                            severity="warning",
                        ).to_dict()
                    )
        return violations


if __name__ == "__main__":
    sys.exit(
        execute_scan_with_workspace(
            LiveAndDeadCodeDistinguishedScanner,
            "live-and-dead-code-are-distinguished",
            build_arch_spec_context,
            skill_root=_ROOT,
        )
    )
