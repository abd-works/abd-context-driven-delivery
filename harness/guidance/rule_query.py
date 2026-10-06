"""The CodeQL query that checks a rule, and the attribution it declares.

A rule's owning practice, fidelity, and pattern are declared as `@practice`,
`@fidelity`, and `@pattern` tags in its query, so a pattern's rules can credit the
parent practice they came from.
"""

from __future__ import annotations

import re
from pathlib import Path

from harness.codeQl_graph.graph import query_pack

_REPO = Path(__file__).resolve().parents[2]
_LERN_PRACTICES = _REPO / "patterns" / "lern_domain_driven" / "practices"
_SOURCE_LANGUAGES = ("python", "javascript", "typescript")
_QUERY_TAG = re.compile(r"^\s*\*\s*@([a-zA-Z_]+)\s+(.+?)\s*$")


class RuleQuery:
    """The `{slug}.ql` that checks one rule, wherever its pack lives."""

    def __init__(self, path: Path) -> None:
        self._path = path
        self._tags: dict[str, str] | None = None

    @staticmethod
    def locate(slug: str, practice: str, language: str) -> RuleQuery | None:
        """The query for this slug, or None when no pack carries one."""
        if practice == "lern_domain_driven":
            found = RuleQuery._in_lern_packs(slug, language)
        else:
            found = RuleQuery._in_practice_packs(slug, practice, language)
        return None if found is None else RuleQuery(found)

    @staticmethod
    def _in_lern_packs(slug: str, language: str) -> Path | None:
        if not _LERN_PRACTICES.is_dir():
            return None
        for child in sorted(_LERN_PRACTICES.iterdir()):
            if not child.is_dir() or child.name.startswith("."):
                continue
            pack = child / "model" / language / "codeql"
            if not (pack / "qlpack.yml").is_file():
                continue
            found = RuleQuery._in_pack(pack, slug)
            if found is not None:
                return found
        return None

    @staticmethod
    def _in_practice_packs(slug: str, practice: str, language: str) -> Path | None:
        ordered = (language, *(name for name in _SOURCE_LANGUAGES if name != language))
        for name in ordered:
            found = RuleQuery._in_pack(query_pack(practice, name), slug)
            if found is not None:
                return found
        return None

    @staticmethod
    def _in_pack(pack: Path, slug: str) -> Path | None:
        rules_root = pack / "rules"
        if not rules_root.is_dir():
            return None
        flat = rules_root / f"{slug}.ql"
        if flat.is_file():
            return flat
        matches = sorted(rules_root.glob(f"**/{slug}.ql"))
        return matches[0] if matches else None

    @property
    def tags(self) -> dict[str, str]:
        if self._tags is None:
            self._tags = self._read_tags()
        return dict(self._tags)

    @property
    def practice(self) -> str:
        return self.tags.get("practice", "")

    @property
    def fidelity(self) -> str:
        return self.tags.get("fidelity", "")

    @property
    def pattern(self) -> str:
        return self.tags.get("pattern", "")

    def _read_tags(self) -> dict[str, str]:
        text = self._path.read_text(encoding="utf-8")
        if not text.startswith("/**"):
            return {}
        end = text.find("*/")
        if end < 0:
            return {}
        found: dict[str, str] = {}
        for line in text[:end].splitlines():
            matched = _QUERY_TAG.match(line)
            if matched:
                found[matched.group(1)] = matched.group(2).strip()
        return found
