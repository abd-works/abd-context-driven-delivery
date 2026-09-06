#!/usr/bin/env python3
"""Check that every term in a story's Domain terms section exists in a domain source artifact.

Scans ``acceptance-criteria.md`` (or the workspace folder containing it), extracts every
term from ``### Domain terms`` sections, then checks each term against every domain source
file found in the same folder.

Domain source files recognised (case-insensitive, any of):
    domain-language.md, domain-language.md, domain-sketch.md,
    domain-model.md, domain-specification.md

Rules enforced:
  1. If ANY domain source exists and a term is not found in any of them → WARNING.
  2. If ANY domain source exists and ``domain-terms.md`` is also present → ERROR.
     (domain-terms.md must not coexist with real domain sources.)
  3. If NO domain source exists at all → WARNING (bootstrap situation; flag to user).

CLI usage (matches all other scanners in this skill):
    python domain-terms-source-scanner.py --workspace <path> [--story-graph <path>]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# ---------------------------------------------------------------------------
# Path bootstrap — mirrors other scanners in this package
# ---------------------------------------------------------------------------
_ROOT = Path(__file__).resolve().parent.parent
_SKILLS = _ROOT.parent
for _p in (
    _SKILLS / "execute-skill-using-skills-rules" / "scripts",
    _SKILLS / "story-graph-ops" / "scripts",
    _ROOT / "scanners",
):
    _s = str(_p)
    if _s not in sys.path:
        sys.path.insert(0, _s)

# ---------------------------------------------------------------------------
# Known domain source filenames (lowercase)
# ---------------------------------------------------------------------------
_DOMAIN_SOURCES = {
    "domain-language.md",
    "domain-language.md",
    "domain-sketch.md",
    "domain-model.md",
    "domain-specification.md",
}

# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------
_STORY_HEADING = re.compile(r"^##\s+Story:\s+(.+)$", re.MULTILINE)
_TERM_LINE = re.compile(r"^\s*-\s+\*([^*]+)\*\s*[—–-]", re.MULTILINE)
_DOMAIN_TERMS_HEADING = re.compile(r"^###\s+Domain terms\s*$", re.MULTILINE | re.IGNORECASE)
_NEXT_SECTION = re.compile(r"^#{2,4}\s+", re.MULTILINE)


# ---------------------------------------------------------------------------
# Artifact discovery
# ---------------------------------------------------------------------------

def _find_domain_sources(folder: Path) -> List[Path]:
    """Return every domain source file found in *folder*."""
    found = []
    for f in folder.iterdir():
        if f.is_file() and f.name.lower() in _DOMAIN_SOURCES:
            found.append(f)
    return found


def _domain_terms_supplement_exists(folder: Path) -> bool:
    return (folder / "domain-terms.md").is_file()


def _build_corpus(sources: List[Path]) -> str:
    parts = []
    for p in sources:
        try:
            parts.append(p.read_text(encoding="utf-8").lower())
        except OSError:
            pass
    return "\n".join(parts)


def _term_in_corpus(term: str, corpus: str) -> bool:
    return term.lower() in corpus


# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def _find_ac_file(workspace: Path) -> Optional[Path]:
    if workspace.is_file():
        return workspace
    for candidate in workspace.glob("*acceptance-criteria.md"):
        return candidate
    return None


def _extract_story_domain_terms(content: str) -> List[Tuple[str, List[str]]]:
    results: List[Tuple[str, List[str]]] = []
    story_starts = list(_STORY_HEADING.finditer(content))
    if not story_starts:
        return results

    for i, story_match in enumerate(story_starts):
        story_name = story_match.group(1).strip()
        block_start = story_match.end()
        block_end = story_starts[i + 1].start() if i + 1 < len(story_starts) else len(content)
        block = content[block_start:block_end]

        dt_match = _DOMAIN_TERMS_HEADING.search(block)
        if not dt_match:
            continue

        section_start = dt_match.end()
        next_heading = _NEXT_SECTION.search(block, section_start)
        section_end = next_heading.start() if next_heading else len(block)
        section_text = block[section_start:section_end]

        terms = [m.group(1).strip() for m in _TERM_LINE.finditer(section_text)]
        if terms:
            results.append((story_name, terms))

    return results


# ---------------------------------------------------------------------------
# Main scan logic
# ---------------------------------------------------------------------------

def scan(workspace: Path) -> List[Tuple[str, str]]:
    """Return list of (severity, message) tuples."""
    violations: List[Tuple[str, str]] = []

    ac_file = _find_ac_file(workspace)
    if ac_file is None:
        return []

    folder = workspace if workspace.is_dir() else workspace.parent
    domain_sources = _find_domain_sources(folder)
    supplement_exists = _domain_terms_supplement_exists(folder)

    # Rule 2: domain-terms.md must not coexist with real domain sources
    if domain_sources and supplement_exists:
        source_names = ", ".join(p.name for p in domain_sources)
        violations.append((
            "ERROR",
            f"`domain-terms.md` exists alongside domain source files ({source_names}). "
            "Merge `domain-terms.md` into the Domain Language and delete it. "
            "NEVER create `domain-terms.md` when any domain source exists."
        ))

    # Rule 3: no domain sources at all
    if not domain_sources:
        violations.append((
            "WARNING",
            "No domain source files found in workspace. "
            "Domain modeling has not been done. "
            "Create a Domain Language before writing AC domain terms, "
            "or use `domain-terms.md` as a temporary bootstrap — flag this to the user."
        ))
        return violations

    # Rule 1: every term must appear in at least one domain source
    content = ac_file.read_text(encoding="utf-8")
    story_terms = _extract_story_domain_terms(content)
    corpus = _build_corpus(domain_sources)
    source_names = ", ".join(p.name for p in domain_sources)

    for story_name, terms in story_terms:
        missing = [t for t in terms if not _term_in_corpus(t, corpus)]
        for term in missing:
            violations.append((
                "WARNING",
                f'Story "{story_name}": term *{term}* not found in any domain source '
                f"({source_names}). "
                "Flag to user — decide: add to Domain Language, use an existing term, or skip."
            ))

    return violations


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check AC domain terms against domain source artifacts."
    )
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--story-graph", type=Path, default=None)
    args = parser.parse_args(argv)
    workspace = args.workspace.resolve()

    violations = scan(workspace)
    for severity, msg in violations:
        print(f"{severity} [domain-terms-source]: {msg}", file=sys.stderr)

    errors = [v for v in violations if v[0] == "ERROR"]
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
