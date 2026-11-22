"""What TDD gives the knowledge graph: the tier each test file is in, the real resources a unit test reaches and the
boundaries it stubs, recorded as facts on the node each file gives (a BDD spec, and a Stories story read from its
acceptance test file); and, on the code those tests drive, whether a test reaches each public operation and names each
declared exception. Its rules then read one fact on one node."""
from __future__ import annotations

import re
from pathlib import Path

from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.source_code.code_reach import CodeReach
from cdd_guidance.practices.source_code.test_files import is_example_code
from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.tdd.tiers import is_code_file, real_resources_in, stubs_in, tier_of
from harness.graph.graph import Graph, Node
from harness.graph.pattern_overlays import GraphOverlay

# The tiers whose examples run a boundary for real.
_REAL_TIERS = ("heavy", "e2e")
# A body that does nothing: only a pass, an ellipsis, or a raise of NotImplementedError. An operation with such a body,
# or with none, as in a model document, is not written yet, so no test is asked of it.
_EMPTY_BODY = re.compile(r"^(?:pass|\.\.\.|raise NotImplementedError(?:\(.*\))?)?$", re.DOTALL)
# The bases every exception class reaches, by the ending of their names.
_EXCEPTION_ENDINGS = ("Error", "Exception", "Warning")
# What TypeScript and JavaScript name a class's constructor, which making the class runs, as Python's __init__.
_SCRIPT_CONSTRUCTOR = "constructor"
_CAPITALISED_WORD = re.compile(r"\b[A-Z]\w+")


class TddOverlay(GraphOverlay):
    """TDD's part of the graph: it adds no nodes, only facts on the test files of the practices it supplements and on
    the code they test."""

    # The practice and node type each test file is read into.
    TEST_FILE_NODES = ((Bdd, "Spec"), (Stories, "Story"))

    def read(self, graph: Graph) -> None:
        if not graph.folder:
            return
        root = Path(graph.folder)
        texts: dict[str, str] = {}
        for practice_class, node_type in self.TEST_FILE_NODES:
            practice = graph.practices.loaded(practice_class)
            if practice is None or practice.reading.in_graph is None:
                continue
            for node in practice.reading.in_graph.nodes(node_type):
                if is_code_file(node.source.file or ""):
                    self._record(node, root / node.source.file, texts)
        if not texts:
            return
        HeavyExamples(graph).record()
        clean = graph.practices.loaded(CleanEngineering)
        if clean is not None and clean.reading.in_graph is not None:
            CodeUnderTest(graph, clean, texts).record()

    def _record(self, node: Node, path: Path, texts: dict[str, str]) -> None:
        """The tier node's file is in, and what a unit test's text shows: the real resources it imports and the
        boundaries it stubs. Each file's text is read once, however many stories it holds."""
        file = node.source.file
        if file not in texts:
            texts[file] = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
        tier = tier_of(file)
        text = texts[file] if tier == "unit" else ""
        node.set_fact("tier", tier)
        node.set_fact("real_resources", real_resources_in(text))
        node.set_fact("stubbed_boundaries", stubs_in(text))


class HeavyExamples:
    """Which of a unit spec's examples a heavy or e2e spec runs for real: an example is the same when it has the same
    should sentence under the same subject, the spec's outermost describe. Each spec keeps its subject and how many of
    its examples have one (``heavy_examples``), so the rule on a spec that stubs a boundary reads one fact."""

    def __init__(self, graph: Graph) -> None:
        self._graph = graph
        bdd = graph.practices.loaded(Bdd)
        self._bdd = bdd.reading.in_graph if bdd is not None else None

    def record(self) -> None:
        if self._bdd is None:
            return
        examples = self._examples_by_file()
        tiers = {spec.source.file: spec.get_fact("tier") for spec in self._bdd.nodes("Spec")}
        real = {example for file, found in examples.items() if tiers.get(file) in _REAL_TIERS for example in found}
        for spec in self._bdd.nodes("Spec"):
            own = examples.get(spec.source.file, {})
            spec.set_fact("subject", next(iter(own.values()), ""))
            spec.set_fact("heavy_examples", len(set(own) & real))

    def _examples_by_file(self) -> dict[str, dict[tuple[str, str], str]]:
        """Each spec file's examples, as (subject, sentence) in lower case, each with its subject as written."""
        found: dict[str, dict[tuple[str, str], str]] = {}
        for observation in self._bdd.nodes("Observation"):
            subject = self._subject_of(observation)
            if subject:
                found.setdefault(observation.source.file, {})[(subject.casefold(), observation.name.strip().casefold())] = subject
        return found

    def _subject_of(self, observation: Node) -> str:
        """The outermost describe an observation sits under; empty for one under none."""
        node, subject = observation, ""
        while node is not None and node.type != "Spec":
            subject = node.name.strip() if node.type == "Description" else subject
            node = self._graph.edges.direct_parent(node)
        return subject


class CodeUnderTest:
    """What the tests the graph read reach in the code Clean Engineering read. A test reaches an operation when an
    observation or a step invokes it, when test code invokes it (a helper a spec calls), when one of the ways the
    project names in its config reaches it (*CodeReach*: a publishing decorator, a registry, an entry point), or when an
    operation a test reaches invokes it. A test names an exception when the class's name is written in a test file or in test code.
    Each public operation that has a body keeps whether a test reaches it (``reached_by_a_test``), and each public
    exception class whether a test names it (``named_by_a_test``); a graph that read no test records neither."""

    def __init__(self, graph: Graph, clean: CleanEngineering, texts: dict[str, str]) -> None:
        self._graph = graph
        self._clean = clean.reading.in_graph
        self._texts = texts

    def record(self) -> None:
        operations = self._clean.nodes("Operation")
        reached = self._reached(operations)
        for operation in operations:
            if self._is_asked_a_test(operation):
                operation.set_fact("reached_by_a_test", id(operation) in reached)
        named = self._names_in_tests(operations)
        for declared in self._clean.nodes("OoadClass"):
            if self._is_production_code(declared) and not declared.name.startswith("_") and self._is_exception(declared, set()):
                declared.set_fact("named_by_a_test", declared.name in named)

    def _reached(self, operations: list[Node]) -> set[int]:
        """Every member a test reaches: those an observation or step invokes, those in test code and those the project's
        ways reach, then every member one of them invokes, followed through Clean Engineering's own invokes links."""
        edges = self._clean.edge_index
        reached = {id(edge.parent): edge.parent for edge in edges.of("invokedBy")}
        reached.update((id(operation), operation) for operation in operations if is_example_code(operation.source.file))
        reached.update((id(operation), operation) for operation in CodeReach.from_graph(self._graph).operations(operations))
        waiting = list(reached.values())
        while waiting:
            for edge in edges.from_parent("invokes", waiting.pop()):
                if id(edge.child) not in reached:
                    reached[id(edge.child)] = edge.child
                    waiting.append(edge.child)
        return set(reached)

    def _is_asked_a_test(self, operation: Node) -> bool:
        """A public operation of production code that has a body: not a private one, a constructor or another
        double-underscore member, a property, or an operation whose body is not written yet."""
        if operation.name.startswith("_") or operation.name == _SCRIPT_CONSTRUCTOR or operation.get_fact("is_private") or operation.get_fact("is_property") or operation.get_fact("is_setter"):
            return False
        # The rule is one of the code fidelity, so an operation its reading recorded at another fidelity is left out; one
        # no reading recorded a fidelity for is judged by its own body.
        if operation.fidelity_read_at not in ("", "code"):
            return False
        return self._is_production_code(operation) and not _EMPTY_BODY.match(str(operation.get_fact("body_text") or "").strip())

    def _is_production_code(self, node: Node) -> bool:
        file = node.source.file or ""
        return is_code_file(file) and not is_example_code(file)

    def _names_in_tests(self, operations: list[Node]) -> set[str]:
        """Each capitalised word a test file or an operation of test code writes: the class names tests can name."""
        words = {word for text in self._texts.values() for word in _CAPITALISED_WORD.findall(text)}
        for operation in operations:
            if is_example_code(operation.source.file):
                words.update(_CAPITALISED_WORD.findall(str(operation.get_fact("body_text") or "")))
        return words

    def _is_exception(self, declared: Node, seen: set[int]) -> bool:
        """Whether a class is an exception: one of its bases, or a base of a base the graph holds, is named as one."""
        if id(declared) in seen:
            return False
        seen.add(id(declared))
        if any(str(base).rsplit(".", 1)[-1].endswith(_EXCEPTION_ENDINGS) for base in declared.get_fact("bases") or []):
            return True
        return any(self._is_exception(edge.child, seen) for edge in self._graph.edges.from_parent("baseClass", declared))
