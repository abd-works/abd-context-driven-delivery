#!/usr/bin/env python3
"""Flag mechanism context files where Participants or Canonical Patterns lack placeholder names.

A mechanism is a templated pattern. Its parameters — the parts that vary per
instance — MUST be visible from the Participants section, the File Structure
section, and the Canonical Patterns section. The template uses placeholder names
such as {Partner}, {System}, {Operation} to mark the parameters.

When these sections are written with one specific instance's concrete names
(e.g. 'MavenirHandler' instead of '{Partner}Handler'), the pattern's variables
become invisible and the reader cannot tell what to change when adding a new
instance.

This scanner checks mechanism context files only (identified by having a
'## Participants' section). It reports a warning when neither Participants,
File Structure, nor Canonical Patterns contains any {placeholder} token.

Note: the scanner does NOT require placeholders in every section — a well-written
parameterized section in *any* of these three is sufficient. It only fires when
ALL three are placeholder-free, which is the strongest signal of a fully concrete
(un-parameterized) write-up.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Optional

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
from arch_spec_context import (  # noqa: E402
    build_arch_spec_context,
    is_mechanism_context,
    extract_section,
)

# A placeholder looks like {Word} or {Multi Word} — curly-brace token
_PLACEHOLDER_RE = re.compile(r"\{[A-Za-z][^}]{0,40}\}")

# Heading aliases for the three key sections
_PARTICIPANTS_NAMES = ("Participants",)
_FILE_STRUCTURE_NAMES = ("File Structure", "Folder Structure", "Structure")
_CANONICAL_NAMES = ("Canonical Patterns", "Canonical Pattern", "Pattern", "Example")


def _has_placeholder(section: Optional[str]) -> bool:
    if not section:
        return False
    return bool(_PLACEHOLDER_RE.search(section))


class MechanismParametersObviousScanner(Scanner):

    def scan_file_with_context(self, context: FileScanContext) -> List[dict]:
        if not context.exists:
            return []
        text = context.file_path.read_text(encoding="utf-8")
        if not is_mechanism_context(text):
            return []

        # Extract the three key sections (try multiple heading aliases)
        participants_text = self._first_section(text, _PARTICIPANTS_NAMES)
        file_structure_text = self._first_section(text, _FILE_STRUCTURE_NAMES)
        canonical_text = self._first_section(text, _CANONICAL_NAMES)

        if any(
            _has_placeholder(s)
            for s in (participants_text, file_structure_text, canonical_text)
        ):
            # At least one section uses placeholders — parameters are visible.
            return []

        # No placeholders found anywhere in the three sections
        folder = context.file_path.parent.name
        found_sections = [
            name
            for name in ("Participants", "File Structure", "Canonical Patterns")
            if self._first_section(text, (name,)) is not None
        ]

        return [
            Violation(
                rule=self.rule,
                violation_message=(
                    f"Mechanism context '{folder}/architecture-context.md' has no "
                    f"{{placeholder}} names in Participants, File Structure, or Canonical Patterns "
                    f"(sections found: {found_sections or 'none'}). "
                    f"Use {{Placeholder}} names (e.g. {{{{Partner}}}}, {{{{Operation}}}}) to make "
                    f"the mechanism's parameters visible so readers know what to change when "
                    f"adding a new instance."
                ),
                location=str(context.file_path),
                severity="warning",
            ).to_dict()
        ]

    @staticmethod
    def _first_section(text: str, names: tuple) -> Optional[str]:
        for name in names:
            result = extract_section(text, name)
            if result is not None:
                return result
        return None


if __name__ == "__main__":
    sys.exit(
        execute_scan_with_workspace(
            MechanismParametersObviousScanner,
            "mechanism-parameters-are-obvious-from-the-pattern",
            build_arch_spec_context,
            skill_root=_ROOT,
        )
    )
