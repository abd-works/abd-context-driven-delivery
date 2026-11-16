"""How BDD takes part in the graph: each spec file's language model reads its describe tree, whose spec, descriptions,
contexts, and observations are added to the graph that holds BDD as they are; then each observation is linked to the
operations and properties of the code it drives."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.annotations.name import Name
from harness.graph.graph import Node
from harness.graph.location import Location
from harness.guidance.practice_reading import PracticeReading
from harness.graph.model_node import schema_sync_paused

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.clean_engineering.model.production_code import is_spec_file, is_test_code

if TYPE_CHECKING:
    from cdd_guidance.practices.bdd.model.bdd_model import BddModel
    from cdd_guidance.practices.bdd.model.nodes import Reach

_BEHAVIOR_EDGES = {"Description": "descriptions", "Context": "contexts", "Observation": "observations"}
# The language a node read from Python names; a script spec drives script code.
_PYTHON = "python"


class BddGraphReading(PracticeReading):
    """How BDD takes part in the graph: it reads each spec file's describe tree, after Clean Engineering's code, then
    links each observation to the code it drives."""

    reads_after = ("clean_engineering",)
    node_types = ("Spec", "Description", "Context", "Observation")

    def read_working_copy(self) -> None:
        """Each spec file's language model reads its describe tree, whose spec, descriptions, contexts, and observations
        are added to its graph as they are; then each observation is linked to the operations and properties of the
        code it drives, when the graph reads Clean Engineering too."""
        root = Path(self.in_graph.source_root)
        specs = [file for file in self.graph.scope.source_files(root, self.practice.formats.suffixes) if is_spec_file(file.name)]
        with schema_sync_paused():
            for index, file in enumerate(specs, start=1):
                relative = file.relative_to(root).as_posix()
                report_progress(f"bdd · specs · {index}/{len(specs)} · {relative}")
                self._add_spec(file, relative)
        clean = self.clean_engineering_reading
        if clean is not None:
            ObservationLinks(self, clean).link()

    @property
    def clean_engineering_reading(self) -> PracticeReading | None:
        """The part of the Clean Engineering practice the graph this practice is read in reads too: the code each
        observation drives; none when the graph reads no Clean Engineering."""
        clean = self.graph.practices.loaded(CleanEngineering) if self.graph is not None else None
        return clean.reading if clean is not None else None

    def _add_spec(self, file: Path, relative: str) -> None:
        """The spec file's describe tree, read by the model of the file's language from the practice's own formats."""
        text = self._spec_text(file)
        if text is None:
            return
        spec = self.practice.formats.for_file(file).parse_code(text)
        spec.load_source_facts(text)
        spec.name = file.stem
        self._add_tree(spec, text.splitlines(), relative)

    def _spec_text(self, file: Path) -> str | None:
        """The spec file's text; none when it cannot be read as UTF-8, so the graph skips it."""
        try:
            return file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return None

    def _add_tree(self, spec: BddModel, lines: list[str], relative: str) -> None:
        """The spec and each node of its describe tree, each at its own lines with the facts its span holds."""
        behavior = spec.behavior_nodes()
        parents = {id(node): node.parent for node in behavior}
        added = {id(spec): self.in_graph.add(spec, f"bdd:Spec:{relative}", Location(relative, 1, max(1, len(lines))))}
        self.graph.edges.link("owns", self.in_graph.root, added[id(spec)])
        for node in behavior:
            node.load_span_facts("\n".join(lines[node.line - 1 : node.end_line]))
            node_id = f"bdd:{node.type}:{relative}:{node.line}:{node.name}"
            added[id(node)] = self.in_graph.add(node, node_id, Location(relative, node.line, node.end_line))
            parent = added.get(id(parents[id(node)]), added[id(spec)])
            self.graph.edges.link(_BEHAVIOR_EDGES[node.type], parent, added[id(node)])


class ObservationLinks:
    """Each observation invokes the operations and properties its realization starts from: what the nearest enclosing
    setup reaches, the event the observation follows, and what the observation's own body calls or reads. Each block
    recorded what its lines reach when its spec was read, so linking reads no file. A name matches only code in the
    spec's own language family, Python or script, and never a spec or a test helper."""

    def __init__(self, bdd: BddGraphReading, clean: PracticeReading) -> None:
        self.bdd = bdd
        self.clean = clean
        self.graph = bdd.graph

    def link(self) -> None:
        by_file: dict[str, list[Node]] = {}
        for node in self.bdd.in_graph.nodes():
            if node.type in _BEHAVIOR_EDGES and node.source.file:
                by_file.setdefault(node.source.file, []).append(node)
        for nodes in by_file.values():
            nodes.sort(key=lambda node: node.source.start_line)
            self._link_file(nodes, nodes[0].file_language == _PYTHON)

    def _link_file(self, nodes: list[Node], is_python: bool) -> None:
        for index, node in enumerate(nodes):
            if node.type != "Observation":
                continue
            invoked = ReachedMembers(self.clean, node.get_fact("reach") or {}, is_python).invoked
            for setup in self._enclosing(nodes, index):
                found = ReachedMembers(self.clean, setup.get_fact("setup_reach") or {}, is_python).invoked
                if found:
                    invoked = found + [member for member in invoked if member not in found]
                    break
            for member in invoked:
                self.graph.edges.relate("invokes", node, member)
                self.graph.edges.relate("invokedBy", member, node)

    def _enclosing(self, nodes: list[Node], index: int) -> list[Node]:
        """Each describe or context around nodes[index], innermost first."""
        observation = nodes[index]
        return [
            parent
            for parent in reversed(nodes[:index])
            if parent.type != "Observation" and parent.source.end_line >= observation.source.end_line
        ]


class ReachedMembers:
    """The code members one block's reach names, in the spec's own language family: Python, or script. A call that
    carries a tool by its name is transport, not the act, so it links to nothing itself."""

    def __init__(self, clean: PracticeReading, reach: Reach, is_python: bool) -> None:
        self._clean = clean
        self._reach = reach
        self._is_python = is_python
        self._reads = set(reach.get("reads", []))
        self._transports = {transport for transport, _toolset, _operation in reach.get("tools", [])}

    @property
    def invoked(self) -> list[Node]:
        """The members the reach names, in the order it names them, one per class and name; a tool it calls by name is
        that toolset's operation."""
        found = self._tool_operations() + [
            member for name in self._reach.get("names", []) for member in self._members_reached(name)
        ]
        unique: dict[tuple[str, str], Node] = {}
        for member in found:
            unique.setdefault((member.get_fact("owner"), member.name), member)
        return list(unique.values())

    def _tool_operations(self) -> list[Node]:
        return [
            member
            for _transport, toolset, operation in self._reach.get("tools", [])
            for member in self._code_members(Name(operation).snake)
            if member.type == "Operation" and Name(member.get_fact("owner")).kebab == toolset
        ]

    def _members_reached(self, name: str) -> list[Node]:
        members = [
            member for member in self._code_members(name)
            # A module function is reached by calling it; a read with its name belongs to some object's field.
            if not (name in self._reads and member.get_fact("owner") == MODULE_FUNCTION_HOLDER)
        ]
        owners = {member.get_fact("owner") for member in members}
        # A name more than two classes share, such as `column`, does not say which one the observation reaches; a read,
        # which has no call to narrow it, links only when one class owns the name.
        if name in self._transports or len(owners) > (1 if name in self._reads else 2):
            return []
        # A getter is both an operation and a property of one class; the operation is the one that runs.
        return sorted(members, key=lambda member: member.type != "Operation")

    def _code_members(self, name: str) -> list[Node]:
        """The code's operations and properties called name in the spec's language family. Specs and the helpers only
        specs use drive the code under test, so an observation never invokes them."""
        return [
            member
            for member in self._clean.code_index.members_named(name)
            if member.source.file
            and not is_test_code(member.source.file)
            and (member.file_language == _PYTHON) == self._is_python
        ]
