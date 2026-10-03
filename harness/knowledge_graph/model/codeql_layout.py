"""Locations of practice CodeQL packs: model/{language}/codeql/{loaders,rules}."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

_REPO = Path(__file__).resolve().parents[3]
_PRACTICES = _REPO / "practices"

SOURCE_LANGUAGES = ("python", "javascript", "typescript")
PACK_FOLDERS = frozenset({"loaders", "rules", "tests"})
EXTRACTOR = {
    "python": "python",
    "javascript": "javascript",
    "typescript": "javascript",
}


def practice_model_root(practice: str) -> Path:
    if practice == "lern_domain_driven":
        return (
            _PRACTICES
            / "clean_engineering"
            / "specifications"
            / "lern_domain_driven"
            / "model"
        )
    return _PRACTICES / practice / "model"


def codeql_pack(practice: str, language: str) -> Path:
    return practice_model_root(practice) / language / "codeql"


def pack_root_for_query(ql_path: Path) -> Path:
    folder = Path(ql_path).parent
    if folder.name in PACK_FOLDERS:
        return folder.parent
    return folder


def rule_query(practice: str, slug: str, language: Optional[str] = None) -> Optional[Path]:
    languages: Iterable[str] = (language,) if language else SOURCE_LANGUAGES
    extra = [lang for lang in SOURCE_LANGUAGES if lang not in languages]
    for lang in (*languages, *extra):
        path = codeql_pack(practice, lang) / "rules" / f"{slug}.ql"
        if path.is_file():
            return path
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
