"""The Clean Engineering graph rules on this repository's own code: every hit lands in production code.

Fixtures written for a spec name their files the way the spec's author expects; this repository names them the way its
authors actually did (`class_channel.feature.py`, `story_test.py`, `catalog-examples/`, `templates/`). So this spec
loads `cdd_guidance/practices` and `harness` through the graph, as validate does, and checks where each hit landed with
its own reading of the file names, kept apart from the rules' own reading so a name the rules miss shows up here.
"""

import re
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import be_above, equal, expect
from mamba import before, description, it

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from cdd_guidance.practices.clean_engineering.model.operation import CONSTRUCTOR_NAMES
from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.ddd.model.stereotypes import BUILDING_BLOCK_KINDS
from harness.graph.graph import Graph

_SCANNED = ["cdd_guidance/practices", "harness"]
# What a file is, by its path from the repository's root.
_SPEC = re.compile(r"(_spec\.(py|js)|\.(spec|test)\.[a-z]+|_test\.py)$|(^|/)(tests?|__tests__|test-utils)/")
_FEATURE_SPEC = re.compile(r"\.feature\.py$")
_TEMPLATE = re.compile(r"(^|/)templates/")
_EXAMPLE = re.compile(r"(^|/)(_examples|catalog-examples|fixtures)/")
# A file a message names, such as the two files of a file cycle: `'order.py'`.
_NAMED_FILE = re.compile(r"'([\w.\-/]+\.(?:py|ts|tsx|js|jsx|java))'")
_PLAIN_JAVASCRIPT = re.compile(r"\.(?:m?js|jsx)$")
# The folder an extension's message says the class it extends comes from: `from 'ddd/model'`.
_EXTENDED_HOME = re.compile(r"from '([^']+)' with")
_COPIED_FIELDS = re.compile(r"copies the fields \[([^\]]*)\]")
_COMPARISON_DUNDERS = frozenset({"__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__"})


class RepositoryScan:
    """Every rule hit the graph keeps on this repository's code, each with the files it lands in: the node's own file,
    and the files its message names inside the node's folder."""

    def __init__(self) -> None:
        graph = Graph()
        practices = [graph.practice_of(kind) for kind in (CleanEngineering, Ddd, Bdd)]
        graph.load_files(str(_REPO), [practice.key for practice in practices], _SCANNED)
        self.clean, self.ddd, self.bdd = (practice.in_graph for practice in practices)
        self.hits: list[tuple[str, list[str]]] = []
        for node in self.clean.nodes():
            for slug in node.rules.failed_slugs:
                self.hits.append((slug, self._files_of(node)))

    def failing(self, in_graph, slug: str) -> list[tuple[object, str]]:
        """Each node of one practice that fails the rule slug, with each message it got."""
        return [
            (node, violation.message)
            for node in in_graph.nodes()
            for violation in node.rules.violations
            if violation.rule == slug
        ]

    def blocks_outside_examples(self) -> list[str]:
        """Each DDD building block read from production code outside an example, as `kind: file`."""
        return sorted(
            f"{kind}: {node.source.file}"
            for kind in BUILDING_BLOCK_KINDS
            for node in self.ddd.nodes(kind)
            if not _EXAMPLE.search((node.source.file or "").replace("\\", "/"))
        )

    def developed_spec_files(self) -> set[str]:
        """The files of the specs BDD read as finished tests."""
        return {spec.source.file for spec in self.bdd.nodes("Spec") if spec.get_fact("developed", False)}

    def _files_of(self, node) -> list[str]:
        own = (node.source.file or "").replace("\\", "/")
        named = [f"{own}/{name}" for violation in node.rules.violations for name in _NAMED_FILE.findall(violation.message)]
        return [own, *named]

    def landing_in(self, kind: re.Pattern) -> list[str]:
        """Each hit, as `rule: file`, that lands in a file of this kind."""
        return sorted({f"{slug}: {file}" for slug, files in self.hits for file in files if kind.search(file)})


with description("the Clean Engineering graph rules on this repository") as self:
    with before.all:
        self.scan = RepositoryScan()

    with it("should find hits in its production code"):
        expect(len(self.scan.hits)).to(be_above(0))

    with it("should find no hit in a spec or test support folder"):
        expect(self.scan.landing_in(_SPEC)).to(equal([]))

    with it("should find no hit in a .feature.py spec"):
        expect(self.scan.landing_in(_FEATURE_SPEC)).to(equal([]))

    with it("should find no hit in a template"):
        expect(self.scan.landing_in(_TEMPLATE)).to(equal([]))

    with it("should find no hit in an example, a catalog example, or a fixture"):
        expect(self.scan.landing_in(_EXAMPLE)).to(equal([]))

    with it("should judge no parameter of plain JavaScript, which has no type syntax"):
        typed = [file for node, _message in self.scan.failing(self.scan.clean, "use-typed-signatures") for file in [node.source.file or ""] if _PLAIN_JAVASCRIPT.search(file)]
        expect(typed).to(equal([]))

    with it("should find no extension kept in a package nested under the domain it extends"):
        nested = [
            node.source.file
            for node, message in self.scan.failing(self.scan.clean, "extensions-live-with-the-domain")
            for home in _EXTENDED_HOME.findall(message)
            if (node.source.file or "").replace("\\", "/").startswith(home.rstrip("/") + "/")
        ]
        expect(nested).to(equal([]))

    with it("should ask no constructor to return a record"):
        constructors = [node.name for node, _message in self.scan.failing(self.scan.clean, "state-change-returns-record-or-named-failure") if node.name in CONSTRUCTOR_NAMES]
        expect(constructors).to(equal([]))

    with it("should find no near copy of a body shorter than three lines"):
        short = [
            node.name
            for node, message in self.scan.failing(self.scan.clean, "eliminate-duplication")
            if "nearly duplicates" in message and node.get_fact("line_count", 0) < 3
        ]
        expect(short).to(equal([]))

    with it("should find no copy of another class's fields shorter than three fields"):
        few = [
            message
            for _node, message in self.scan.failing(self.scan.clean, "do-not-invent-parallel-object-models")
            for copied in _COPIED_FIELDS.findall(message)
            if len([field for field in copied.split(",") if field.strip()]) < 3
        ]
        expect(few).to(equal([]))

    with it("should find no reach into private state in a comparison dunder"):
        reaching = [node.name for node, _message in self.scan.failing(self.scan.clean, "hide-inner-details") if node.name in _COMPARISON_DUNDERS]
        expect(reaching).to(equal([]))

    with it("should read no DDD building block from a folder no bounded context or stereotype marks as a domain"):
        expect(self.scan.blocks_outside_examples()).to(equal([]))

    with it("should judge no finished spec by the rules of a behavior sketch"):
        finished = self.scan.developed_spec_files()
        judged = sorted(
            f"{slug}: {node.source.file}"
            for slug in ("no-implementation", "framework-syntax")
            for node, _message in self.scan.failing(self.scan.bdd, slug)
            if node.source.file in finished
        )
        expect(judged).to(equal([]))
