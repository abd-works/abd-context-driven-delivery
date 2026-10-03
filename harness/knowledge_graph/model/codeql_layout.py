"""Locations of practice CodeQL packs: model/{language}/codeql/{loaders,rules}."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Iterable, Optional

_REPO = Path(__file__).resolve().parents[3]
_PRACTICES = _REPO / "practices"

SOURCE_LANGUAGES = ("python", "javascript", "typescript")
PACK_FOLDERS = frozenset({"loaders", "rules", "tests"})
RULE_QUERY_FOLDERS = ("rules",)
_LERN_ROOT = _REPO / "patterns" / "lern_domain_driven"
EXTRACTOR = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "javascript",
}


def practice_model_root(practice: str) -> Path:
    return _PRACTICES / practice / "model"


def lern_spec_root() -> Path:
    return _LERN_ROOT


def lern_practices_root() -> Path:
    return lern_spec_root() / "practices"


def lern_codeql_pack(attributed_practice: str, language: str) -> Path:
    return lern_practices_root() / attributed_practice / "model" / language / "codeql"


def lern_codeql_packs(language: str) -> list[Path]:
    packs: list[Path] = []
    root = lern_practices_root()
    if not root.is_dir():
        return packs
    for child in sorted(root.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        pack = child / "model" / language / "codeql"
        if (pack / "qlpack.yml").is_file():
            packs.append(pack)
    return packs


def locate_lern_rule_query(slug: str, language: str = "typescript") -> Optional[Path]:
    for pack in lern_codeql_packs(language):
        found = locate_rule_query(pack, slug)
        if found is not None:
            return found
    return None


def codeql_pack(practice: str, language: str) -> Path:
    return practice_model_root(practice) / language / "codeql"


def pack_root_for_query(ql_path: Path) -> Path:
    folder = Path(ql_path).resolve().parent
    while folder != folder.parent:
        if (folder / "qlpack.yml").is_file():
            return folder
        folder = folder.parent
    folder = Path(ql_path).parent
    if folder.name in PACK_FOLDERS:
        return folder.parent
    return folder


_QUERY_TAG = re.compile(r"^\s*\*\s*@([a-zA-Z_]+)\s+(.+?)\s*$")


def parse_query_metadata(ql_path: Path) -> Dict[str, str]:
    text = Path(ql_path).read_text(encoding="utf-8")
    meta: Dict[str, str] = {}
    if not text.startswith("/**"):
        return meta
    end = text.find("*/")
    if end < 0:
        return meta
    for line in text[:end].splitlines():
        matched = _QUERY_TAG.match(line)
        if matched:
            meta[matched.group(1)] = matched.group(2).strip()
    return meta


def _rule_query_roots(pack: Path) -> list[Path]:
    return [pack / name for name in RULE_QUERY_FOLDERS if (pack / name).is_dir()]


def locate_rule_query(pack: Path, slug: str) -> Optional[Path]:
    for rules_root in _rule_query_roots(pack):
        flat = rules_root / f"{slug}.ql"
        if flat.is_file():
            return flat
        matches = sorted(rules_root.glob(f"**/{slug}.ql"))
        if matches:
            return matches[0]
    return None


def rule_stems_in_pack(pack: Path) -> set[str]:
    stems: set[str] = set()
    for rules_root in _rule_query_roots(pack):
        stems.update(path.stem for path in rules_root.rglob("*.ql"))
    return stems


def rule_query(practice: str, slug: str, language: Optional[str] = None) -> Optional[Path]:
    languages: Iterable[str] = (language,) if language else SOURCE_LANGUAGES
    extra = [lang for lang in SOURCE_LANGUAGES if lang not in languages]
    for lang in (*languages, *extra):
        found = locate_rule_query(codeql_pack(practice, lang), slug)
        if found is not None:
            return found
    return None


def loader_query(practice: str, name: str, language: str) -> Path:
    return codeql_pack(practice, language) / "loaders" / f"{name}.ql"


def has_graph_query(practice: str, slug: str) -> bool:
    return rule_query(practice, slug) is not None


def qlpack_name(practice: str, language: str) -> str:
    return f"cdd/{practice.replace('_', '-')}-graph-query-{language}"


def extractor_language(language: str) -> str:
    return EXTRACTOR.get(language, language)


def source_language_from_path(path: Path) -> str | None:
    parts = Path(path).resolve().parts
    for index, part in enumerate(parts):
        if part == "codeql" and index > 0 and parts[index - 1] in SOURCE_LANGUAGES:
            return parts[index - 1]
    return None


def listed_practices() -> tuple[str, ...]:
    return (
        "stories",
        "clean_engineering",
        "ddd",
        "bdd",
        "ux",
        "lern_domain_driven",
    )
