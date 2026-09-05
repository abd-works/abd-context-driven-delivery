"""Simple protocol-driven CLI for story graph operations.

The CLI keeps one flow for every command:
1) load canonical StoryMap from the requested protocol
2) optionally transform through another protocol
3) run operation
4) write output

Batch operations are intentionally small and explicit. They operate on the
canonical StoryMap and support moving/copying whole SubEpic trees (including
all nested SubEpics, Stories, and AcceptanceCriteria).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

_HERE = Path(__file__).resolve()
_PROJECT_ROOT = _HERE.parent.parent.parent
import sys

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, SubEpic
from src.core.stories.story_map import StoryMap
from src.core.stories.update_report import ChangeKind, UpdateReport
from src.formats.code.java.java_story_map import JavaStoryMap
from src.formats.code.python.python_story_map import PythonStoryMap
from src.formats.code.typescript.typescript_story_map import TypeScriptStoryMap
from src.formats.diagram.drawio.drawio_story_map import DrawIOStoryMap
from src.formats.diagram.miro.miro_story_map import MiroStoryMap
from src.formats.document.json.json_story_map import JsonStoryMap
from src.formats.document.markdown.markdown_story_map import MarkdownStoryMap


class CliError(Exception):
    """Raised when CLI inputs are invalid."""


@dataclass(frozen=True)
class ProtocolSpec:
    name: str
    external_kind: str  # "text" | "tree"


PROTOCOLS: Dict[str, ProtocolSpec] = {
    "json": ProtocolSpec("json", "text"),
    "markdown": ProtocolSpec("markdown", "text"),
    "drawio": ProtocolSpec("drawio", "text"),
    "miro": ProtocolSpec("miro", "text"),
    "typescript": ProtocolSpec("typescript", "tree"),
    "python": ProtocolSpec("python", "tree"),
    "java": ProtocolSpec("java", "tree"),
}

CODE_PROTOCOLS = {"typescript", "python", "java"}


def _adapter_for(protocol: str):
    if protocol == "json":
        return JsonStoryMap()
    if protocol == "markdown":
        return MarkdownStoryMap()
    if protocol == "drawio":
        return DrawIOStoryMap()
    if protocol == "miro":
        return MiroStoryMap()
    if protocol == "typescript":
        return TypeScriptStoryMap()
    if protocol == "python":
        return PythonStoryMap()
    if protocol == "java":
        return JavaStoryMap()
    raise CliError(f"Unsupported protocol: {protocol}")


def _read_external(path: Path, protocol: str):
    spec = PROTOCOLS[protocol]
    if not path.is_file():
        raise CliError(f"Input file does not exist: {path}")
    raw = path.read_text(encoding="utf-8")
    if spec.external_kind == "text":
        return raw
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise CliError(
            f"Tree protocol '{protocol}' expects JSON object at {path}"
        ) from exc
    if not isinstance(payload, dict):
        raise CliError(
            f"Tree protocol '{protocol}' expects an object mapping path -> content"
        )
    for key, value in payload.items():
        if not isinstance(key, str) or not isinstance(value, str):
            raise CliError(
                f"Tree protocol '{protocol}' expects string path -> string content"
            )
    return payload


def _write_external(path: Path, protocol: str, external: Any) -> None:
    spec = PROTOCOLS[protocol]
    path.parent.mkdir(parents=True, exist_ok=True)
    if spec.external_kind == "text":
        if not isinstance(external, str):
            raise CliError(f"Protocol '{protocol}' must render text")
        path.write_text(external, encoding="utf-8")
        return
    if not isinstance(external, dict):
        raise CliError(f"Protocol '{protocol}' must render path->content tree")
    path.write_text(json.dumps(external, indent=2) + "\n", encoding="utf-8")


def _load_story_map(path: Path, protocol: str) -> StoryMap:
    adapter = _adapter_for(protocol)
    external = _read_external(path, protocol)
    return adapter.parse(external)


def _render_story_map(story_map: StoryMap, protocol: str):
    adapter = _adapter_for(protocol)
    return adapter.render(story_map)


def _sync_external(canonical: StoryMap, path: Path, protocol: str) -> UpdateReport:
    adapter = _adapter_for(protocol)
    external = _read_external(path, protocol)
    return adapter.sync(external, canonical)


def _assert_conversion_policy(from_protocol: str, to_protocol: str) -> None:
    # WHY: once code exists, code files are the source of truth because users
    # hand-edit them. The CLI must not regenerate code from model/document
    # protocols where those edits cannot be preserved.
    if to_protocol in CODE_PROTOCOLS and from_protocol not in CODE_PROTOCOLS:
        raise CliError(
            "Model/document -> code conversion is disabled. "
            "Code protocols are source-of-truth after generation; use AI skills "
            "for controlled regeneration and merge."
        )


def _renumber(items: Sequence[Any], start: int = 1) -> None:
    for index, item in enumerate(items, start=start):
        item.sequential_order = index


def _clone_acceptance_criteria(ac: AcceptanceCriteria) -> AcceptanceCriteria:
    return AcceptanceCriteria(ac.name, ac.sequential_order, ac.text)


def _clone_story(story: Story) -> Story:
    cloned = Story(story.name, story.sequential_order, story.story_type)
    cloned.users = list(story.users)
    cloned.acceptance_criteria = [
        _clone_acceptance_criteria(ac) for ac in story.acceptance_criteria
    ]
    return cloned


def _clone_sub_epic(sub_epic: SubEpic) -> SubEpic:
    cloned = SubEpic(sub_epic.name, sub_epic.sequential_order)
    cloned.test_file = sub_epic.test_file
    cloned.domain_concepts = list(sub_epic.domain_concepts)
    cloned.sub_epics = [_clone_sub_epic(nested) for nested in sub_epic.sub_epics]
    cloned.stories = [_clone_story(story) for story in sub_epic.stories]
    return cloned


def _find_epic(story_map: StoryMap, epic_name: str) -> Epic:
    for epic in story_map.epics:
        if epic.name == epic_name:
            return epic
    raise CliError(f"Epic not found: {epic_name}")


def _find_sub_epic_with_parent_lists(
    epic: Epic, sub_epic_name: str
) -> Optional[tuple[SubEpic, List[SubEpic]]]:
    def walk(items: List[SubEpic]) -> Optional[tuple[SubEpic, List[SubEpic]]]:
        for sub_epic in items:
            if sub_epic.name == sub_epic_name:
                return sub_epic, items
            nested = walk(sub_epic.sub_epics)
            if nested is not None:
                return nested
        return None

    return walk(epic.sub_epics)


def _copy_sub_epic(
    story_map: StoryMap, from_epic: str, sub_epic: str, to_epic: str
) -> None:
    source_epic = _find_epic(story_map, from_epic)
    target_epic = _find_epic(story_map, to_epic)
    located = _find_sub_epic_with_parent_lists(source_epic, sub_epic)
    if located is None:
        raise CliError(f"SubEpic '{sub_epic}' not found under Epic '{from_epic}'")
    source_sub_epic, _ = located
    copied = _clone_sub_epic(source_sub_epic)
    target_epic.sub_epics.append(copied)
    _renumber(target_epic.sub_epics)


def _move_sub_epic(
    story_map: StoryMap, from_epic: str, sub_epic: str, to_epic: str
) -> None:
    source_epic = _find_epic(story_map, from_epic)
    target_epic = _find_epic(story_map, to_epic)
    located = _find_sub_epic_with_parent_lists(source_epic, sub_epic)
    if located is None:
        raise CliError(f"SubEpic '{sub_epic}' not found under Epic '{from_epic}'")
    source_sub_epic, source_parent_list = located
    source_parent_list.remove(source_sub_epic)
    _renumber(source_parent_list)
    target_epic.sub_epics.append(source_sub_epic)
    _renumber(target_epic.sub_epics)


def _copy_epic_children(story_map: StoryMap, from_epic: str, to_epic: str) -> None:
    source_epic = _find_epic(story_map, from_epic)
    target_epic = _find_epic(story_map, to_epic)
    for sub_epic in source_epic.sub_epics:
        target_epic.sub_epics.append(_clone_sub_epic(sub_epic))
    _renumber(target_epic.sub_epics)


def _move_epic_children(story_map: StoryMap, from_epic: str, to_epic: str) -> None:
    source_epic = _find_epic(story_map, from_epic)
    target_epic = _find_epic(story_map, to_epic)
    moving = list(source_epic.sub_epics)
    source_epic.sub_epics = []
    _renumber(source_epic.sub_epics)
    target_epic.sub_epics.extend(moving)
    _renumber(target_epic.sub_epics)


def _apply_batch_operations(
    story_map: StoryMap, operations: Iterable[Dict[str, Any]]
) -> StoryMap:
    for index, operation in enumerate(operations, start=1):
        op_type = operation.get("type")
        if op_type == "copy_sub_epic":
            _copy_sub_epic(
                story_map=story_map,
                from_epic=operation["from_epic"],
                sub_epic=operation["sub_epic"],
                to_epic=operation["to_epic"],
            )
        elif op_type == "move_sub_epic":
            _move_sub_epic(
                story_map=story_map,
                from_epic=operation["from_epic"],
                sub_epic=operation["sub_epic"],
                to_epic=operation["to_epic"],
            )
        elif op_type == "copy_epic_children":
            _copy_epic_children(
                story_map=story_map,
                from_epic=operation["from_epic"],
                to_epic=operation["to_epic"],
            )
        elif op_type == "move_epic_children":
            _move_epic_children(
                story_map=story_map,
                from_epic=operation["from_epic"],
                to_epic=operation["to_epic"],
            )
        else:
            raise CliError(
                f"Unsupported operation type at index {index}: {op_type!r}"
            )
    return story_map


def _load_operations(path: Path) -> List[Dict[str, Any]]:
    if not path.is_file():
        raise CliError(f"Operations file does not exist: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise CliError(f"Operations file is not valid JSON: {path}") from exc
    if isinstance(payload, list):
        operations = payload
    elif isinstance(payload, dict) and isinstance(payload.get("operations"), list):
        operations = payload["operations"]
    else:
        raise CliError("Operations JSON must be a list or {\"operations\": [...]}")
    for operation in operations:
        if not isinstance(operation, dict):
            raise CliError("Every operation must be an object")
    return operations


def _format_report(report: UpdateReport) -> str:
    lines: List[str] = []
    changes = [c for c in report.changes if c.kind != ChangeKind.EXACT_MATCH]
    if not changes:
        return "No changes."
    lines.append(f"Changes: {len(changes)}")
    for change in changes:
        if change.kind == ChangeKind.ADD:
            lines.append(f"- ADD {change.node_name} (parent={change.parent_name})")
        elif change.kind == ChangeKind.REMOVE:
            lines.append(f"- REMOVE {change.node_name} (parent={change.parent_name})")
        elif change.kind == ChangeKind.RENAME:
            lines.append(f"- RENAME {change.from_name} -> {change.to_name}")
        elif change.kind == ChangeKind.REORDER:
            lines.append(f"- REORDER {change.from_name} -> {change.to_name}")
    return "\n".join(lines)


def cmd_convert(args: argparse.Namespace) -> int:
    _assert_conversion_policy(args.from_protocol, args.to_protocol)
    canonical = _load_story_map(Path(args.input), args.from_protocol)
    rendered = _render_story_map(canonical, args.to_protocol)
    _write_external(Path(args.output), args.to_protocol, rendered)
    return 0


def cmd_sync(args: argparse.Namespace) -> int:
    canonical_path = Path(args.canonical)
    canonical = _load_story_map(canonical_path, "json")
    report = _sync_external(canonical, Path(args.external), args.protocol)
    if args.write_canonical:
        rendered = _render_story_map(canonical, "json")
        _write_external(canonical_path, "json", rendered)
    print(_format_report(report))
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    graph_path = Path(args.graph)
    canonical = _load_story_map(graph_path, "json")
    operations = _load_operations(Path(args.operations))
    _apply_batch_operations(canonical, operations)
    rendered = _render_story_map(canonical, "json")
    output_path = Path(args.output) if args.output else graph_path
    _write_external(output_path, "json", rendered)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Protocol-driven StoryGraph CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    protocol_names = sorted(PROTOCOLS.keys())

    convert = subparsers.add_parser("convert", help="Convert one protocol to another")
    convert.add_argument("--from-protocol", choices=protocol_names, required=True)
    convert.add_argument("--to-protocol", choices=protocol_names, required=True)
    convert.add_argument("--input", required=True)
    convert.add_argument("--output", required=True)
    convert.set_defaults(func=cmd_convert)

    sync = subparsers.add_parser(
        "sync", help="Sync canonical graph from external protocol artifact"
    )
    sync.add_argument("--canonical", required=True, help="Path to story-graph.json")
    sync.add_argument("--protocol", choices=protocol_names, required=True)
    sync.add_argument("--external", required=True)
    sync.add_argument("--write-canonical", action="store_true")
    sync.set_defaults(func=cmd_sync)

    batch = subparsers.add_parser(
        "batch", help="Apply batch graph operations from operations JSON"
    )
    batch.add_argument("--graph", required=True, help="Path to story-graph.json")
    batch.add_argument("--operations", required=True, help="Path to operations JSON")
    batch.add_argument("--output", help="Optional output file (defaults to --graph)")
    batch.set_defaults(func=cmd_batch)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except CliError as exc:
        parser.error(str(exc))
    except KeyError as exc:
        parser.error(f"Missing required operation field: {exc}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
