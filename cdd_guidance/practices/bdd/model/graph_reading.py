"""How BDD takes part in the graph: each spec file's language model reads its describe tree, whose spec, descriptions,
contexts, and observations are added to the graph that holds BDD as they are; then each observation is linked to the
operations and properties of the code it drives, and each describe to the class it describes. A spec reaches code
only through what its own imports name, never through a name alone."""

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
from cdd_guidance.practices.clean_engineering.model.imported_classes import ImportedClasses
from cdd_guidance.practices.clean_engineering.model.production_code import is_spec_file, is_test_code
from cdd_guidance.practices.clean_engineering.model.script_imports import ClassReference, ScriptImports
from cdd_guidance.practices.clean_engineering.model.source_facts import CONSTRUCTOR_NAMES

if TYPE_CHECKING:
    from cdd_guidance.practices.bdd.model.bdd_model import BddModel
    from cdd_guidance.practices.bdd.model.nodes import Reach

_BEHAVIOR_EDGES = {"Description": "descriptions", "Context": "contexts", "Observation": "observations"}
# The language a node read from Python names; a script spec drives script code.
_PYTHON = "python"
_ARTICLES = ("a ", "an ", "the ")


class BddGraphReading(PracticeReading):
    """How BDD takes part in the graph: it reads each spec file's describe tree, after Clean Engineering's code, then
    links each observation to the code it drives."""

    reads_after = ("clean_engineering",)
    node_types = ("Spec", "Description", "Context", "Observation")
    # A describe's states and observations are listed as its spec writes them, in turn, not kind by kind.
    source_ordered_types = frozenset({"Description", "Context", "Observation"})

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
        self._record_developed_specs()
        clean = self.clean_engineering_reading
        if clean is not None:
            ObservationLinks(self, clean).link()

    def _record_developed_specs(self) -> None:
        """Whether each description and observation sits in a finished spec (``in_developed_spec``), one whose every
        signature has its test body, which the behavior fidelity's rules then leave alone."""
        finished = {spec.source.file for spec in self.in_graph.nodes("Spec") if spec.get_fact("developed", False)}
        for kind in ("Observation", "Context"):
            for node in self.in_graph.nodes(kind):
                node.set_fact("in_developed_spec", node.source.file in finished)

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
        spec.imported_classes = [list(reference) for reference in ScriptImports(text).class_references(file, Path(self.in_graph.source_root))]
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
    setup reaches, the event the observation follows, and what the observation's own body calls or reads. Each describe
    aligns with the class it describes. Each block recorded what its lines reach when its spec was read, so linking
    reads no file. A name is looked for only in the code the spec's own imports name."""

    def __init__(self, bdd: BddGraphReading, clean: PracticeReading) -> None:
        self.bdd = bdd
        self.clean = clean
        self.graph = bdd.graph
        code_classes = [node for node in clean.in_graph.nodes("OoadClass") if node.source.file and not is_test_code(node.source.file)]
        # A spec imports classes of its own language family, Python or script, so each family is resolved apart: a
        # script's `./order` is `order.ts` though `order.py` lies beside it. No re-export is followed.
        self._imported_classes = {
            is_python: ImportedClasses([node for node in code_classes if (node.file_language == _PYTHON) == is_python], {})
            for is_python in (True, False)
        }

    def link(self) -> None:
        by_file: dict[str, list[Node]] = {}
        for node in self.bdd.in_graph.nodes():
            if node.type in _BEHAVIOR_EDGES and node.source.file:
                by_file.setdefault(node.source.file, []).append(node)
        specs = {spec.source.file: spec for spec in self.bdd.in_graph.nodes("Spec")}
        for file, nodes in by_file.items():
            nodes.sort(key=lambda node: node.source.start_line)
            spec = specs[file]
            self._link_file(nodes, ImportedCode(self.clean, self._imported_classes[spec.file_language == _PYTHON], spec))

    def _link_file(self, nodes: list[Node], imported: ImportedCode) -> None:
        for index, node in enumerate(nodes):
            if node.type == "Description":
                self._align(node, imported)
            if node.type != "Observation":
                continue
            enclosing = self._enclosing(nodes, index)
            reaches = [setup.get_fact("setup_reach") or {} for setup in enclosing]
            own = node.get_fact("reach") or {}
            builds: dict[str, str] = {}
            for reach in [*reversed(reaches), own]:
                builds.update(reach.get("builds", {}))
            invoked = ReachedMembers(imported, own, builds).invoked
            # The nearest block that has a setup gives the event; a block with none passes to the one around it.
            setup = next((reach for reach in reaches if reach.get("names")), None)
            if setup is not None:
                found = ReachedMembers(imported, setup, builds).invoked
                invoked = found + [member for member in invoked if member not in found]
            for member in invoked:
                self.graph.edges.relate("invokes", node, member)
                self.graph.edges.relate("invokedBy", member, node)

    def _align(self, described: Node, imported: ImportedCode) -> None:
        subject = imported.class_described_by(described.name)
        if subject is not None:
            self.graph.edges.relate("alignsWith", described, subject)

    def _enclosing(self, nodes: list[Node], index: int) -> list[Node]:
        """Each describe or context around nodes[index], innermost first."""
        observation = nodes[index]
        return [
            parent
            for parent in reversed(nodes[:index])
            if parent.type != "Observation" and parent.source.end_line >= observation.source.end_line
        ]


class ImportedCode:
    """The code one spec's imports name: the classes it imports, and the operations and properties of the files those
    imports name, in the spec's own language family, Python or script. A spec and the helpers only specs use drive the
    code under test, so they are never part of it."""

    def __init__(self, clean: PracticeReading, classes: ImportedClasses, spec: Node) -> None:
        self._clean = clean
        self._is_python = spec.file_language == _PYTHON
        references = [ClassReference(*pair) for pair in spec.get_fact("imported_classes") or []]
        resolved = [classes.resolve(reference, spec.source.file) for reference in references]
        self.classes = [node for node in resolved if node is not None]
        # A module a spec imports a function from holds no class the import names, so its file is taken as written.
        self._files = {node.source.file for node in self.classes} | {file for reference in references for file in reference.files()}

    def members_named(self, name: str) -> list[Node]:
        """The operations and properties called name in the files the spec imports from."""
        return [
            member
            for member in self._clean.code_index.members_named(name)
            if member.source.file in self._files
            and not is_test_code(member.source.file)
            and (member.file_language == _PYTHON) == self._is_python
        ]

    def tool_operations(self, toolset: str, operation: str) -> list[Node]:
        """The operation called operation of the toolset a tool's name gives, in the spec's language family."""
        return [
            member
            for member in self._clean.code_index.members_named(operation)
            if member.type == "Operation"
            and Name(member.get_fact("owner")).kebab == toolset
            and member.source.file
            and not is_test_code(member.source.file)
            and (member.file_language == _PYTHON) == self._is_python
        ]

    def constructors_of(self, class_name: str) -> list[Node]:
        """The constructor of the imported class called class_name, when its code writes one."""
        files = {node.source.file for node in self.classes if node.name == class_name}
        return [
            member
            for constructor in sorted(CONSTRUCTOR_NAMES)
            for member in self.members_named(constructor)
            if member.get_fact("owner") == class_name and member.source.file in files
        ]

    def class_described_by(self, subject: str) -> Node | None:
        """The imported class a describe's subject opens with, `an order` or `a cart line that is new`; the longest
        name when several fit, none when no imported class is named."""
        words = subject.strip().lower()
        words = next((words[len(article) :] for article in _ARTICLES if words.startswith(article)), words)
        named = [node for node in self.classes if f"{words} ".startswith(f"{Name(node.name).snake.replace('_', ' ')} ")]
        return max(named, key=lambda node: len(node.name), default=None)


class ReachedMembers:
    """The code members one block's reach names, among the code its spec imports. A call that carries a tool by its
    name is transport, not the act, so it links to nothing itself."""

    def __init__(self, imported: ImportedCode, reach: Reach, builds: dict[str, str]) -> None:
        self._imported = imported
        self._reach = reach
        # The class each variable in scope was built or declared as, by the block's own lines and the setups around it.
        self._builds = builds
        self._reads = set(reach.get("reads", []))
        self._transports = {transport for transport, _toolset, _operation in reach.get("tools", [])}

    @property
    def invoked(self) -> list[Node]:
        """The members the reach names, in the order it names them, one per class and name; a tool it calls by name is
        that toolset's operation."""
        found = self._tool_operations() + [
            member for name in self._reach.get("names", []) for member in self._members_reached(name)
        ]
        unique: dict[tuple[str, str, str], Node] = {}
        for member in found:
            unique.setdefault((member.source.file, member.get_fact("owner"), member.name), member)
        return list(unique.values())

    def _tool_operations(self) -> list[Node]:
        """A tool is named by its toolset and operation, which is its address, so it is found without an import."""
        return [
            member
            for _transport, toolset, operation in self._reach.get("tools", [])
            for member in self._imported.tool_operations(toolset, Name(operation).snake)
        ]

    def _members_reached(self, name: str) -> list[Node]:
        constructors = self._imported.constructors_of(name)
        if constructors:
            return constructors
        members = [
            member for member in self._imported.members_named(name)
            # A module function is reached by calling it; a read with its name belongs to some object's field.
            if not (name in self._reads and member.get_fact("owner") == MODULE_FUNCTION_HOLDER)
        ]
        members = self._of_receiver(name, members)
        owners = {member.get_fact("owner") for member in members}
        # A name more than two classes share, such as `column`, does not say which one the observation reaches; a read,
        # which has no call to narrow it, links only when one class owns the name.
        if name in self._transports or len(owners) > (1 if name in self._reads else 2):
            return []
        # A getter is both an operation and a property of one class; the operation is the one that runs.
        return sorted(members, key=lambda member: member.type != "Operation")

    def _of_receiver(self, name: str, members: list[Node]) -> list[Node]:
        """The members of the class the name's receiver was built as, when a setup or the block itself built it."""
        built = {self._builds[receiver] for receiver in self._reach.get("receivers", {}).get(name, []) if receiver in self._builds}
        of_built = [member for member in members if member.get_fact("owner") in built]
        return of_built or members
