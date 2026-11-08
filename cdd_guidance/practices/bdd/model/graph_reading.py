"""How BDD takes part in the graph: each spec file's language model reads its describe tree, whose spec, descriptions,
contexts, and observations are added to the graph that holds BDD as they are; then each observation is linked to the
operations and properties of the code it drives."""

from __future__ import annotations

from pathlib import Path

from harness.annotations.name import Name
from harness.graph.graph import Graph, Node
from harness.graph.model_node import schema_sync_paused

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.model.production_code import is_spec_file, is_test_code

_BEHAVIOR_EDGES = {"Description": "descriptions", "Context": "contexts", "Observation": "observations"}


class BddGraphReading:
    """BDD's operations over the graph it is read in: reading each spec file's describe tree, then linking each
    observation to the code it drives."""

    graph: Graph

    def read_working_copy(self) -> None:
        """Each spec file's language model reads its describe tree, whose spec, descriptions, contexts, and observations
        are added to its graph as they are."""
        root = Path(self.in_graph.source_root)
        specs = [file for file in self.graph.source_files(root, self.readable_suffixes) if is_spec_file(file.name)]
        with schema_sync_paused():
            for index, file in enumerate(specs, start=1):
                relative = file.relative_to(root).as_posix()
                self.graph.report_progress(f"bdd · specs · {index}/{len(specs)} · {relative}")
                self._add_spec(file, relative)

    def link_to_other_practices(self) -> None:
        """Link each observation to the operations and properties of the code it drives, when the graph reads Clean
        Engineering too."""
        clean = self.clean_engineering_practice
        if clean is not None:
            ObservationLinks(self, clean).link()

    @property
    def clean_engineering_practice(self) -> CleanEngineering | None:
        """The Clean Engineering practice the graph this practice is read in reads too: the code each observation
        drives; none when the graph reads no Clean Engineering."""
        return self.graph.loaded(CleanEngineering) if self.graph is not None else None

    def _add_spec(self, file: Path, relative: str) -> None:
        """The spec file's describe tree, each node at its own lines with the facts its span holds, read by the model of
        the file's language from the practice's own formats."""
        try:
            text = file.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        spec = self.format_for(file).parse_code(text)
        spec.load_source_facts(text)
        lines = text.splitlines()
        behavior = spec.behavior_nodes()
        parents = {id(node): node.parent for node in behavior}
        spec.name = file.stem
        graph = self.graph
        added = {id(spec): self.in_graph.add(spec, f"bdd:Spec:{relative}", relative, 1, max(1, len(lines)))}
        graph.link("owns", self.in_graph.root, added[id(spec)])
        for node in behavior:
            node.load_span_facts("\n".join(lines[node.line - 1 : node.end_line]))
            node_id = f"bdd:{node.type}:{relative}:{node.line}:{node.name}"
            added[id(node)] = self.in_graph.add(node, node_id, relative, node.line, node.end_line)
            parent = added.get(id(parents[id(node)]), added[id(spec)])
            graph.link(_BEHAVIOR_EDGES[node.type], parent, added[id(node)])


class ObservationLinks:
    """Each observation invokes the operations and properties its realization starts from: what the nearest enclosing
    setup reaches, the event the observation follows, and what the observation's own body calls or reads. Each block
    recorded what its lines reach when its spec was read, so linking reads no file. A name matches only code in the
    spec's own language family, Python or script, and never a spec or a test helper."""

    def __init__(self, bdd: BddGraphReading, clean: CleanEngineering) -> None:
        self.bdd = bdd
        self.clean = clean
        self.graph = bdd.graph
        self.members: dict[tuple[bool, str], list] = {}
        for node in [*clean.in_graph.nodes("Operation"), *clean.in_graph.nodes("Property")]:
            if node.source.file and not is_test_code(node.source.file):
                self.members.setdefault((_is_python(node), node.name), []).append(node)

    def link(self) -> None:
        by_file: dict[str, list] = {}
        for node in self.bdd.in_graph.nodes():
            if node.type in _BEHAVIOR_EDGES and node.source.file:
                by_file.setdefault(node.source.file, []).append(node)
        for nodes in by_file.values():
            nodes.sort(key=lambda node: node.source.start_line)
            self._link_file(nodes, _is_python(nodes[0]))

    def _link_file(self, nodes: list, is_python: bool) -> None:
        for index, node in enumerate(nodes):
            if node.type != "Observation":
                continue
            invoked = self._invoked_by(node.get_fact("reach") or {}, is_python)
            for setup in _enclosing(nodes, index):
                found = self._invoked_by(setup.get_fact("setup_reach") or {}, is_python)
                if found:
                    invoked = found + [member for member in invoked if member not in found]
                    break
            for member in invoked:
                self.graph.link("invokes", node, member, "relationship")
                self.graph.link("invokedBy", member, node, "relationship")

    def _invoked_by(self, reach: dict, is_python: bool) -> list:
        """The members a block's reach names, in the order it names them, one per class and name; a tool it calls by
        name is that toolset's operation, and the call carrying it is transport, not the act."""
        invoked: list = []
        seen: set[tuple[str, str]] = set()

        def add(member) -> None:
            key = (member.get_fact("owner"), member.name)
            if key not in seen:
                seen.add(key)
                invoked.append(member)

        transports = set()
        for transport, toolset, operation in reach.get("tools", []):
            transports.add(transport)
            for member in self.members.get((is_python, Name(operation).snake), ()):
                if member.type == "Operation" and Name(member.get_fact("owner")).kebab == toolset:
                    add(member)
        reads = set(reach.get("reads", []))
        for name in reach.get("names", []):
            for member in self._members_reached(name, is_python, reads, transports):
                add(member)
        return invoked

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


def _is_python(node: Node) -> bool:
    """Whether the node was read from Python, which its file's language says; a script spec drives script code."""
    return node.file_language == "python"


def _enclosing(nodes: list, index: int) -> list:
    """Each describe or context around nodes[index], innermost first."""
    observation = nodes[index]
    return [
        parent
        for parent in reversed(nodes[:index])
        if parent.type != "Observation" and parent.source.end_line >= observation.source.end_line
    ]
