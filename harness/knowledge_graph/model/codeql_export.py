"""Typed CodeQL practice-graph export — JSON on disk or in-memory query rows."""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any


@dataclass
class CodeQLClass:
    module: str = ""
    name: str = ""
    file: str = ""
    line: int = 0
    stereotypes: list[str] = field(default_factory=list)


@dataclass
class CodeQLProperty:
    class_name: str = ""
    name: str = ""
    type_hint: str = ""
    file: str = ""
    line: int = 0


@dataclass
class CodeQLOperation:
    class_name: str = ""
    name: str = ""
    return_type: str = ""
    file: str = ""
    line: int = 0
    parameters: list[str] = field(default_factory=list)


@dataclass
class CodeQLCall:
    caller_class: str = ""
    caller_operation: str = ""
    callee_class: str = ""
    callee_operation: str = ""
    caller_file: str = ""
    caller_line: int = 0


@dataclass
class CodeQLStoryCall:
    story_file: str = ""
    line: int = 0
    callee_class: str = ""
    callee_operation: str = ""
    phase: str = ""
    step_text: str = ""


@dataclass
class CodeQLStoryObservation:
    story_file: str = ""
    line: int = 0
    target_class: str = ""
    target_member: str = ""
    member_kind: str = ""
    phase: str = ""


@dataclass
class CodeQLStory:
    text: str = ""
    file: str = ""
    epic: str = ""
    sub_epic: str = ""
    line: int = 0


@dataclass
class CodeQLScenario:
    text: str = ""
    story: str = ""
    file: str = ""
    line: int = 0


@dataclass
class CodeQLBackground:
    text: str = ""
    story: str = ""
    file: str = ""
    line: int = 0
    end_line: int = 0
    scope: str = "each"


@dataclass
class CodeQLStep:
    keyword: str = ""
    text: str = ""
    file: str = ""
    line: int = 0
    story: str = ""
    scenario: str = ""
    background: str = ""
    phase: str = ""


@dataclass
class CodeQLExampleExport:
    export_name: str = ""
    file: str = ""
    demonstrates: list[str] = field(default_factory=list)
    line: int = 0
    owner: str = ""
    owner_kind: str = ""


@dataclass
class CodeQLPracticeGraphExport:
    version: int = 1
    classes: list[CodeQLClass] = field(default_factory=list)
    properties: list[CodeQLProperty] = field(default_factory=list)
    operations: list[CodeQLOperation] = field(default_factory=list)
    calls: list[CodeQLCall] = field(default_factory=list)
    story_calls: list[CodeQLStoryCall] = field(default_factory=list)
    story_observations: list[CodeQLStoryObservation] = field(default_factory=list)
    example_exports: list[CodeQLExampleExport] = field(default_factory=list)
    stories: list[CodeQLStory] = field(default_factory=list)
    scenarios: list[CodeQLScenario] = field(default_factory=list)
    backgrounds: list[CodeQLBackground] = field(default_factory=list)
    steps: list[CodeQLStep] = field(default_factory=list)


_LIST_TYPES = {
    "classes": CodeQLClass,
    "properties": CodeQLProperty,
    "operations": CodeQLOperation,
    "calls": CodeQLCall,
    "story_calls": CodeQLStoryCall,
    "story_observations": CodeQLStoryObservation,
    "example_exports": CodeQLExampleExport,
    "stories": CodeQLStory,
    "scenarios": CodeQLScenario,
    "backgrounds": CodeQLBackground,
    "steps": CodeQLStep,
}


def _row(cls: type, raw: Any) -> Any:
    if not isinstance(raw, dict):
        return cls()
    allowed = {item.name for item in fields(cls)}
    return cls(**{key: value for key, value in raw.items() if key in allowed})


def load_codeql_export(path: str | Path) -> CodeQLPracticeGraphExport:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return CodeQLPracticeGraphExport()
    kwargs: dict[str, Any] = {}
    if "version" in data:
        kwargs["version"] = int(data["version"] or 1)
    for name, row_type in _LIST_TYPES.items():
        rows = data.get(name) or []
        kwargs[name] = [_row(row_type, row) for row in rows if isinstance(row, dict)]
    return CodeQLPracticeGraphExport(**kwargs)


def resolve_codeql_results_path(
    root: str | Path,
    results_path: str | Path | None = None,
) -> Path | None:
    if results_path is not None:
        path = Path(results_path)
        return path if path.is_file() else None
    candidate = Path(root) / ".codeql" / "results" / "practice-graph.json"
    return candidate if candidate.is_file() else None
