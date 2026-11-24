"""How BDD takes part in the graph: each spec file's language model reads its describe tree, whose spec, descriptions,
contexts, and observations are added to the graph that holds BDD as they are; then each observation is linked to the
operations and properties of the code it drives, and each describe to the class it describes. A spec reaches code
only through what its own imports name, never through a name alone."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.annotations.name import Name
from harness.graph.graph import Node
from harness.graph.location import Location
from harness.graph.practice_node_types import PracticeNodeTypes
from harness.graph.practice_reading import PracticeReading
from harness.graph.model_node import schema_sync_paused

from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.reading.node_evidence import NodeEvidence
from cdd_guidance.practices.clean_engineering.reading.code_file import CodeFile, CodeSpan
from cdd_guidance.practices.source_code import HoldsProjectTestCode
from cdd_guidance.practices.source_code import ClassReference, ScriptImports

if TYPE_CHECKING:
    from harness.graph.model_node import ModelNode

    from cdd_guidance.practices.bdd.model.bdd_model import BddModel

_BEHAVIOR_EDGES = {"Description": "descriptions", "Context": "contexts", "Observation": "observations"}
# The language a node read from Python names; a script spec drives script code.
_PYTHON = "python"
_ARTICLES = ("a ", "an ", "the ")
# A tool called by its name, `<toolset>.<operation>`: `call("ticket.move_next", ticket="pet-visits")`.
_TOOL_NAMED = re.compile(r"""\b(\w+)\(\s*["']([a-z][a-z-]*)\.([a-zA-Z_]+)["']""")
_QUOTED = re.compile(r"""(['"`])(?:\\.|(?!\1).)*\1""")
# A mamba spec's own state, `self.cart`, which its blocks reach as a local.
_SPEC_STATE = re.compile(r"\bself\.(\w+)")
# A block that runs after each observation or after them all: `with after.each:`, `afterEach(() => {`.
_PYTHON_TEARDOWN = re.compile(r"^(\s*)with\s+after\.(?:each|all)\b")
_SCRIPT_TEARDOWN = re.compile(r"^\s*after(?:Each|All)\s*\(")


class BddNodeTypes(PracticeNodeTypes):
    """BDD's node types: an observation ``invokes`` the members its source calls and ``demonstrates`` what it names. A
    spec lists its descriptions, a description its contexts, and a context its observations and examples."""

    child_lists = frozenset({"descriptions", "contexts", "observations", "examples"})
    edge_order = {"descriptions": 1, "contexts": 2, "observations": 3, "demonstrates": 4, "specifies": 4, "examples": 5, "invokes": 12}
    evidence_kinds = frozenset({"invokes", "demonstrates"})

    def links(self, owner: ModelNode, kind: str, target: ModelNode) -> bool:
        evidence = NodeEvidence(owner)
        if kind == "invokes":
            return evidence.invokes(target.name)
        return kind == "demonstrates" and evidence.mentions(target.name)


class BddGraphReading(HoldsProjectTestCode, PracticeReading):
    """How BDD takes part in the graph: it reads each spec file's describe tree, after Clean Engineering's code, then
    links each observation to the code it drives."""

    reads_after = (CleanEngineering,)
    node_types = ("Spec", "Description", "Context", "Observation")
    types = BddNodeTypes()
    # A describe's states and observations are listed as its spec writes them, in turn, not kind by kind.
    source_ordered_types = frozenset({"Description", "Context", "Observation"})

    def read_working_copy(self) -> None:
        """Each spec file's language model reads its describe tree, whose spec, descriptions, contexts, and observations
        are added to its graph as they are; then each observation is linked to the operations and properties of the
        code it drives, when the graph reads Clean Engineering too."""
        root = Path(self.in_graph.source_root)
        specs = [file for file in self.graph.scope.source_files(root, self.practice.formats.suffixes) if self.test_code.is_spec(file)]
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
        # The fidelity each spec was read at, by what it holds: finished test bodies are development, signatures are
        # behavior. A realization's call graphs are not told apart from behavior here. Its blocks answer the spec's.
        for spec in self.in_graph.nodes("Spec"):
            spec.read_at("development" if spec.source.file in finished else "behavior")
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
    setup calls, the event the observation follows, and what the observation's own body calls or reads. Each describe
    aligns with the class it describes. A spec's code is resolved by the spec's own file as Clean Engineering's index
    knows it, given the classes the spec imports (``CodeFile.members_called_in``), so an observation invokes the member
    a call in the code it drives would invoke; a spec and the helpers only specs use drive the code under test, so they
    are never part of it, and a tool called by its name is that toolset's operation."""

    def __init__(self, bdd: BddGraphReading, clean: PracticeReading) -> None:
        self.bdd = bdd
        self.clean = clean
        self.graph = bdd.graph

    def link(self) -> None:
        by_file: dict[str, list[Node]] = {}
        for node in self.bdd.in_graph.nodes():
            if node.type in _BEHAVIOR_EDGES and node.source.file:
                by_file.setdefault(node.source.file, []).append(node)
        specs = {spec.source.file: spec for spec in self.bdd.in_graph.nodes("Spec")}
        for file, nodes in by_file.items():
            nodes.sort(key=lambda node: node.source.start_line)
            spec = specs[file]
            imports = [ClassReference(*pair) for pair in spec.get_fact("imported_classes") or []]
            _SpecLinks(self, nodes, self.clean.code_index.file(file, imports), spec.file_language == _PYTHON).link()


class _SpecLinks:
    """The links of one spec file's blocks, read through the spec's own file."""

    def __init__(self, links: ObservationLinks, nodes: list[Node], code_file: CodeFile, is_python: bool) -> None:
        self._graph = links.graph
        self._index = links.clean.code_index
        self._test_code = links.bdd.test_code
        self._nodes = nodes
        self._file = code_file
        self._is_python = is_python

    def link(self) -> None:
        for index, node in enumerate(self._nodes):
            if node.type == "Description":
                self._align(node)
            if node.type != "Observation":
                continue
            enclosing = self._enclosing(index)
            setups = [self._setup_code(block) for block in enclosing]
            own = _SpecCode(node.source.text)
            # The setups run before the observation, outermost first, so each makes the locals the observation uses.
            before = "\n".join(code.code for code in reversed(setups))
            invoked = self._tool_operations(own) + self._called_in(own, before)
            # The nearest block that has a setup gives the event; a block with none passes to the one around it.
            at = next((index for index, code in enumerate(setups) if code.code.strip()), None)
            if at is not None:
                setup = setups[at]
                found = self._tool_operations(setup) + self._called_in(setup, "\n".join(code.code for code in reversed(setups[at + 1:])))
                invoked = found + [member for member in invoked if member not in found]
            for member in dict.fromkeys(invoked):
                self._graph.edges.relate("invokes", node, member)
                self._graph.edges.relate("invokedBy", member, node)

    def _called_in(self, code: "_SpecCode", before: str) -> list[Node]:
        """The members of the code under test the code calls and reads, after the code before it; a call that carries
        a tool by its name is transport, not the act, so it is none of them."""
        return [
            member for member in self._file.members_called_in(CodeSpan(code.code, None, {}, before))
            if member.source.file and not self._test_code.is_test_code(member.source.file) and member.name not in code.transports
        ]

    def _tool_operations(self, code: "_SpecCode") -> list[Node]:
        """A tool is named by its toolset and operation, which is its address, so it is found without an import: the
        operation of the toolset a tool's name gives, in the spec's language family."""
        return [
            member
            for toolset, operation in code.tools
            for member in self._index.members_named(Name(operation).snake)
            if member.type == "Operation"
            and Name(member.get_fact("owner")).kebab == toolset
            and member.source.file
            and not self._test_code.is_test_code(member.source.file)
            and (member.file_language == _PYTHON) == self._is_python
        ]

    def _align(self, described: Node) -> None:
        """A describe aligns with the imported class its subject opens with, `an order` or `a cart line that is new`;
        the longest name when several fit, none when no imported class is named."""
        words = described.name.strip().lower()
        words = next((words[len(article):] for article in _ARTICLES if words.startswith(article)), words)
        imported = [node for node in self._file.imported_classes if not self._test_code.is_test_code(node.source.file)]
        named = [node for node in imported if f"{words} ".startswith(f"{Name(node.name).snake.replace('_', ' ')} ")]
        subject = max(named, key=lambda node: len(node.name), default=None)
        if subject is not None:
            self._graph.edges.relate("alignsWith", described, subject)

    def _enclosing(self, index: int) -> list[Node]:
        """Each describe or context around the node at index, innermost first."""
        observation = self._nodes[index]
        return [
            parent
            for parent in reversed(self._nodes[:index])
            if parent.type != "Observation" and parent.source.end_line >= observation.source.end_line
        ]

    def _setup_code(self, block: Node) -> "_SpecCode":
        """A describe's or context's own lines, after its opening line and before its first child."""
        start, end = block.source.start_line, block.source.end_line
        first_child = min((node.source.start_line for node in self._nodes if start < node.source.start_line <= end), default=end + 1)
        return _SpecCode("\n".join(_without_teardown(block.source.text.splitlines()[1:first_child - start])))


class _SpecCode:
    """A spec's lines as code: each tool its calls carry by name, the calls that carry them, and the code itself, without
    its strings, with the spec's own state on `self` read as locals, since a mamba spec keeps its fixtures there."""

    def __init__(self, text: str) -> None:
        named = [(match.group(1), match.group(2), match.group(3)) for match in _TOOL_NAMED.finditer(text)]
        self.tools = [(toolset, operation) for _transport, toolset, operation in named]
        self.transports = {transport for transport, _toolset, _operation in named}
        self.code = _SPEC_STATE.sub(r"\1", _QUOTED.sub('""', CodeSpan.code_of(text)))


def _without_teardown(lines: list[str]) -> list[str]:
    """A block's lines without those that run after its observations, which clean up what the observation did and are
    no part of the event it observes."""
    teardown = _Teardown()
    return [line for line in lines if not teardown.holds(line)]


class _Teardown:
    """The teardown a walk down a block's lines is inside: a Python ``with after.each`` block, known by the indent of its
    opening line, or a script ``afterEach(`` call, known by the brackets still open; outside one, neither."""

    _SCRIPT = "script"

    def __init__(self) -> None:
        self._inside: str | None = None
        self._open_brackets = 0

    def holds(self, line: str) -> bool:
        """Whether line belongs to a teardown: one it opens, or one an earlier line opened and this line continues."""
        if self._inside == self._SCRIPT:
            return self._continues_script(line)
        if self._inside is not None and self._continues_python(line):
            return True
        self._inside = None
        return self._opens(line)

    def _continues_script(self, line: str) -> bool:
        self._open_brackets += _bracket_balance(line)
        if self._open_brackets <= 0:
            self._inside = None
        return True

    def _continues_python(self, line: str) -> bool:
        """A blank line, or one indented deeper than the ``with after.each`` that opened the teardown."""
        return not line.strip() or len(line) - len(line.lstrip()) > len(self._inside or "")

    def _opens(self, line: str) -> bool:
        python = _PYTHON_TEARDOWN.match(line)
        if python is not None:
            self._inside = python.group(1)
            return True
        if _SCRIPT_TEARDOWN.match(line):
            self._open_brackets = _bracket_balance(line)
            self._inside = self._SCRIPT if self._open_brackets > 0 else None
            return True
        return False


def _bracket_balance(line: str) -> int:
    """How many more round brackets line opens than it closes."""
    return line.count("(") - line.count(")")
