"""CodeQL practice-graph export — JSON contract for the populate pass."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class CodeQLClass:
    module: str
    name: str
    file: str = ""
    line: int = 0
    stereotypes: List[str] = field(default_factory=list)


@dataclass
class CodeQLProperty:
    class_name: str
    name: str
    type_hint: str = ""
    file: str = ""
    line: int = 0


@dataclass
class CodeQLOperation:
    class_name: str
    name: str
    return_type: str = ""
    file: str = ""
    line: int = 0
    parameters: List[str] = field(default_factory=list)


@dataclass
class CodeQLCall:
    """Resolved call edge between domain operations."""

    caller_class: str
    caller_operation: str
    callee_class: str
    callee_operation: str
    caller_file: str = ""
    caller_line: int = 0


@dataclass
class CodeQLStoryCall:
    """Call from a story test file at a line — join to GraphStep by source location."""

    story_file: str
    line: int
    callee_class: str
    callee_operation: str
    phase: str = ""  # given | when | then
    step_text: str = ""


@dataclass
class CodeQLExampleExport:
    """Example factory export demonstrates one or more domain classes."""

    export_name: str
    file: str
    demonstrates: List[str] = field(default_factory=list)
    line: int = 0


@dataclass
class CodeQLStoryObservation:
    """Property or operation read/assert in a story test — join to GraphStep."""

    story_file: str
    line: int
    target_class: str
    target_member: str  # property or operation name
    member_kind: str = "property"  # property | operation
    phase: str = "then"


@dataclass
class CodeQLPracticeGraphExport:
    """Facts extracted once from a CodeQL database — consumed by populate."""

    version: int = 1
    classes: List[CodeQLClass] = field(default_factory=list)
    properties: List[CodeQLProperty] = field(default_factory=list)
    operations: List[CodeQLOperation] = field(default_factory=list)
    calls: List[CodeQLCall] = field(default_factory=list)
    story_calls: List[CodeQLStoryCall] = field(default_factory=list)
    story_observations: List[CodeQLStoryObservation] = field(default_factory=list)
    example_exports: List[CodeQLExampleExport] = field(default_factory=list)


def load_codeql_export(path: Path) -> CodeQLPracticeGraphExport:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return CodeQLPracticeGraphExport(
        version=int(raw.get("version", 1)),
        classes=[CodeQLClass(**c) for c in raw.get("classes", [])],
        properties=[CodeQLProperty(**p) for p in raw.get("properties", [])],
        operations=[CodeQLOperation(**o) for o in raw.get("operations", [])],
        calls=[CodeQLCall(**c) for c in raw.get("calls", [])],
        story_calls=[CodeQLStoryCall(**s) for s in raw.get("story_calls", [])],
        story_observations=[
            CodeQLStoryObservation(**o) for o in raw.get("story_observations", [])
        ],
        example_exports=[CodeQLExampleExport(**e) for e in raw.get("example_exports", [])],
    )


def resolve_codeql_results_path(root: Path, override: Optional[Path] = None) -> Optional[Path]:
    """Locate CodeQL export JSON under the workspace."""
    if override is not None:
        candidate = Path(override).resolve()
        return candidate if candidate.is_file() else None
    for relative in (
        ".codeql/results/practice-graph.json",
        ".codeql/results/practice-graph.bqrs.json",
    ):
        candidate = root / relative
        if candidate.is_file():
            return candidate
    return None
