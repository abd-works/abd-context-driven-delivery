"""How BDD takes part in the graph: each spec file's language model reads its describe tree, whose spec, descriptions,
contexts, and observations are added to the graph that holds BDD as they are; then each observation is linked to the
operations and properties of the code it drives."""

from __future__ import annotations

import re
from pathlib import Path

from harness.annotations.name import Name
from harness.graph.model_node import schema_sync_paused
from typing import TYPE_CHECKING

from harness.graph.graph import Graph

if TYPE_CHECKING:
    from cdd_guidance.practices.bdd.bdd import Bdd

_CODE_SUFFIXES = {".ts", ".tsx", ".js", ".jsx", ".py"}
_BEHAVIOR_EDGES = {"Description": "descriptions", "Context": "contexts", "Observation": "observations"}
_MEMBER_CALL = re.compile(r"\.([\w$]+)\s*\(")
# A member read that is not a call: `ticketOn(page, OTHER).isLocked`, `stage.actions`.
_MEMBER_READ = re.compile(r"\.([\w$]+)\b(?!\s*\()")
_BARE_CALL = re.compile(r"(?<![.\w])([A-Za-z_]\w*)\s*\(")
# A tool called by its name, `<toolset>.<operation>`: `call("ticket.move_next", ticket="pet-visits")`.
_TOOL_NAMED = re.compile(r"""\b(\w+)\(\s*["']([a-z][a-z-]*)\.([a-zA-Z_]+)["']""")
_QUOTED = re.compile(r"""(['"`])(?:\\.|(?!\1).)*\1""")
_SPEC_STATE = re.compile(r"\bself\.(\w+)")


def read_specs(practice: Bdd) -> None:
    """Add the describe tree of each spec file the graph reads to the graph that holds BDD."""
    from cdd_guidance.practices.bdd.model.spec_source import is_spec_file

    root = Path(practice.graph.source_root_of(practice))
    specs = [file for file in practice.graph.source_files(root, _CODE_SUFFIXES) if is_spec_file(file)]
    with schema_sync_paused():
        for index, file in enumerate(specs, start=1):
            relative = file.relative_to(root).as_posix()
            practice.graph.report_progress(f"bdd · specs · {index}/{len(specs)} · {relative}")
            _add_spec(practice, file, relative)


def link_observations(graph: Graph) -> None:
    """Link each observation to the Clean Engineering members it drives, when the graph holds both practices."""
    if "bdd" in graph.practices and "clean_engineering" in graph.practices:
        _ObservationLinks(graph).link()


def _add_spec(practice: Bdd, file: Path, relative: str) -> None:
    """The spec file's describe tree, each node at its own lines with the facts its span holds."""
    from cdd_guidance.practices.bdd.model.code_spec_model import PythonBddModel, TypeScriptBddModel

    try:
        text = file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return
    spec = (PythonBddModel() if file.suffix == ".py" else TypeScriptBddModel()).parse_code(text)
    spec.load_source_facts(text)
    lines = text.splitlines()
    behavior = spec.behavior_nodes()
    parents = {id(node): node.parent for node in behavior}
    spec.name = file.stem
    spec.type = "Spec"
    graph = practice.graph
    added = {id(spec): graph.add(practice, spec, f"bdd:Spec:{relative}", relative, 1, max(1, len(lines)))}
    graph.link("owns", graph.root_of(practice), added[id(spec)])
    for node in behavior:
        node.load_span_facts("\n".join(lines[node.line - 1 : node.end_line]))
        node_id = f"bdd:{node.type}:{relative}:{node.line}:{node.name}"
        added[id(node)] = graph.add(practice, node, node_id, relative, node.line, node.end_line)
        parent = added.get(id(parents[id(node)]), added[id(spec)])
        graph.link(_BEHAVIOR_EDGES[node.type], parent, added[id(node)])


def _is_test_support(path: str) -> bool:
    """Spec files and the helpers only specs use: they drive the code under test, so an observation never invokes them."""
    from cdd_guidance.practices.bdd.model.spec_source import is_spec_file

    return is_spec_file(Path(path)) or "/tests/" in f"/{path}" or "/test-utils/" in f"/{path}" or "page-driver" in path


class _ObservationLinks:
    """Each observation invokes the operations and properties its realization starts from: what the nearest enclosing
    setup calls, the event the observation follows, and what the observation's own body calls or reads. A name matches
    only code in the spec's own language, and never a spec or a test helper."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.bdd = graph.practice("bdd")
        self.clean = graph.practice("clean_engineering")
        self.members: dict[tuple[bool, str], list] = {}
        for node in [*graph.nodes_of(self.clean, "Operation"), *graph.nodes_of(self.clean, "Property")]:
            if node.source.file and not _is_test_support(node.source.file):
                self.members.setdefault((node.source.file.endswith(".py"), node.name), []).append(node)

    def link(self) -> None:
        by_file: dict[str, list] = {}
        for node in self.graph.nodes_of(self.bdd):
            if node.type in _BEHAVIOR_EDGES and node.source.file:
                by_file.setdefault(node.source.file, []).append(node)
        for file, nodes in by_file.items():
            nodes.sort(key=lambda node: node.source.start_line)
            path = self.graph.loaded_folder / file if self.graph.loaded_folder is not None else None
            lines = path.read_text(encoding="utf-8").splitlines() if path and path.is_file() else []
            self._link_file(nodes, lines, file.endswith(".py"))

    def _link_file(self, nodes: list, lines: list[str], is_python: bool) -> None:
        starts = [node.source.start_line for node in nodes]
        for index, node in enumerate(nodes):
            if node.type != "Observation":
                continue
            invoked = self._invoked_in("\n".join(lines[node.source.start_line - 1 : node.source.end_line]), is_python)
            for setup in _enclosing_setups(nodes, starts, index, lines):
                found = self._invoked_in(setup, is_python)
                if found:
                    invoked = found + [member for member in invoked if member not in found]
                    break
            for member in invoked:
                self.graph.link("invokes", node, member, "relationship")
                self.graph.link("invokedBy", member, node, "relationship")

    def _invoked_in(self, text: str, is_python: bool) -> list:
        """The members text reaches, in the order it names them, one per class and name; a tool it calls by name
        (``call("ticket.move_next", …)``) is that toolset's operation, and the call carrying it is transport, not the act."""
        invoked: list = []
        seen: set[tuple[str, str]] = set()

        def add(member) -> None:
            key = (member.get_fact("owner"), member.name)
            if key not in seen:
                seen.add(key)
                invoked.append(member)

        transports = self._tools_named(text, is_python, add)
        # A mamba spec keeps its fixtures on `self`; `self.project` is the spec's own state, not a member of the code.
        code = _SPEC_STATE.sub(r"\1", _QUOTED.sub('""', text))
        calls = _MEMBER_CALL.findall(code) + _BARE_CALL.findall(code)
        reads = set(_MEMBER_READ.findall(code)) - set(calls)
        for name in dict.fromkeys(_ordered_names(code)):
            for member in self._members_reached(name, is_python, reads, transports):
                add(member)
        return invoked

    def _tools_named(self, text: str, is_python: bool, add) -> set[str]:
        transports: set[str] = set()
        for match in _TOOL_NAMED.finditer(text):
            transports.add(match.group(1))
            for member in self.members.get((is_python, Name(match.group(3)).snake), ()):
                if member.type == "Operation" and Name(member.get_fact("owner")).kebab == match.group(2):
                    add(member)
        return transports

    def _members_reached(self, name: str, is_python: bool, reads: set[str], transports: set[str]) -> list:
        members = [
            member for member in self.members.get((is_python, name), ())
            # A module function is reached by calling it; a read with its name belongs to some object's field.
            if not (name in reads and member.get_fact("owner") == "_module")
        ]
        owners = {member.get_fact("owner") for member in members}
        # A name more than two classes share, such as `column`, does not say which one the observation reaches; a read,
        # which has no call to narrow it, links only when one class owns the name.
        if name in transports or len(owners) > (1 if name in reads else 2):
            return []
        # A getter is both an operation and a property of one class; the operation is the one that runs.
        return sorted(members, key=lambda member: member.type != "Operation")


def _ordered_names(code: str) -> list[str]:
    """Every member name code calls or reads, in the order it names them."""
    found = [(match.start(1), match.group(1)) for pattern in (_MEMBER_CALL, _MEMBER_READ, _BARE_CALL) for match in pattern.finditer(code)]
    return [name for _start, name in sorted(found)]


def _enclosing_setups(nodes: list, starts: list[int], index: int, lines: list[str]) -> list[str]:
    """The setup text of each describe or context around nodes[index], innermost first: its lines up to its first child."""
    observation = nodes[index]
    setups = []
    for position in range(index - 1, -1, -1):
        parent = nodes[position]
        if parent.type == "Observation" or parent.source.end_line < observation.source.end_line:
            continue
        first_child = next((start for start in starts[position + 1 :] if start > parent.source.start_line), parent.source.end_line)
        setups.append("\n".join(lines[parent.source.start_line : first_child - 1]))
    return setups
