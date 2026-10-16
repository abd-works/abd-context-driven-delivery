"""Schema types and relationship fields for one practice, including a selected overlay.

The loader reads this catalog. It does not name node types or edge types itself.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from harness.graph.graph import resolve_overlay_root
from harness.graph.schema_rules import semantic_type

_REPO = Path(__file__).resolve().parents[2]
_SKIP = {"is", "name", "path", "fidelity", "rules", "where", "id", "text", "order"}
_TYPE_HEADER = re.compile(r"^(?:([A-Za-z]\w*):|(\s+)-\s+([A-Za-z]\w*):)\s*$")
_FIELD = re.compile(r"^\s+-?\s*([A-Za-z]\w*)\??:\s*(.+)$")
_PLACEHOLDER = re.compile(r"\{[^}]+\}")


@dataclass(frozen=True)
class SchemaType:
    practice: str
    key: str
    semantic: str
    is_ref: str
    path: str
    fields: tuple[tuple[str, tuple[str, ...]], ...]


def practice_schema(practice: str, overlays: list[str]) -> tuple[SchemaType, ...]:
    """Base schema, then each selected overlay schema for this practice."""
    found: list[SchemaType] = []
    base = _REPO / "practices" / practice / "model" / "schema.yaml"
    if base.is_file():
        found.extend(parse_schema(practice, base.read_text(encoding="utf-8")))
    for overlay in overlays:
        root = resolve_overlay_root(overlay)
        schema = root / "practices" / practice / "model" / "schema.yaml"
        if schema.is_file():
            found.extend(parse_schema(practice, schema.read_text(encoding="utf-8")))
    return tuple(found)


def overlay_schema(overlays: list[str]) -> tuple[SchemaType, ...]:
    """Types declared by the selected pattern overlays."""
    found: list[SchemaType] = []
    for overlay in overlays:
        root = resolve_overlay_root(overlay)
        practices = root / "practices"
        if not practices.is_dir():
            continue
        for schema in sorted(practices.glob("*/model/schema.yaml")):
            practice = schema.parents[1].name
            found.extend(parse_schema(practice, schema.read_text(encoding="utf-8")))
    return tuple(found)


def parse_schema(practice: str, text: str) -> list[SchemaType]:
    drafts: dict[str, dict] = {}
    order: list[str] = []
    owner = ""
    for line in text.splitlines():
        header = _TYPE_HEADER.match(line)
        if header:
            key = header.group(1) or header.group(3)
            if key in _SKIP:
                continue
            owner = key
            if key not in drafts:
                drafts[key] = {"is": "", "path": "", "fields": []}
                order.append(key)
            continue
        if not owner:
            continue
        field = _FIELD.match(line)
        if field is None:
            continue
        _store_field(drafts[owner], field.group(1), field.group(2).strip())
    return [_schema_type(practice, key, drafts[key]) for key in order]


def path_matches(template: str, relative: Path) -> bool:
    """A path template with a literal suffix names a file. A directory template does not."""
    if not template or template.endswith("/"):
        return False
    literal = _PLACEHOLDER.sub("", template).strip("/")
    if not literal:
        return False
    pattern = _PLACEHOLDER.sub(r".+", template.strip("/"))
    target = relative.name if "." in template else relative.stem
    return re.fullmatch(pattern, target) is not None


def _store_field(draft: dict, name: str, value: str) -> None:
    if name == "is":
        draft["is"] = value.split()[0]
        return
    if name == "path":
        draft["path"] = value.strip().strip('"')
        return
    if name in _SKIP:
        return
    targets = _type_refs(value)
    if targets:
        draft["fields"].append((name, tuple(targets)))


def _type_refs(value: str) -> list[str]:
    if value.startswith('"'):
        return []
    found: list[str] = []
    for token in re.findall(r"[A-Za-z]\w*(?:\.[A-Za-z]\w*)?", value):
        name = token.split(".")[-1]
        if name in {"string", "number", "dotPath"} or name in found:
            continue
        found.append(name)
    return found


def _schema_type(practice: str, key: str, draft: dict) -> SchemaType:
    return SchemaType(
        practice,
        key,
        semantic_type(key),
        draft["is"],
        draft["path"],
        tuple(draft["fields"]),
    )
