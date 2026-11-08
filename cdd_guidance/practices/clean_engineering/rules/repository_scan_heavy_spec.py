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
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from harness.graph.graph import Graph

_SCANNED = ["cdd_guidance/practices", "harness"]
# What a file is, by its path from the repository's root.
_SPEC = re.compile(r"(_spec\.(py|js)|\.(spec|test)\.[a-z]+|_test\.py)$|(^|/)(tests?|__tests__|test-utils)/")
_FEATURE_SPEC = re.compile(r"\.feature\.py$")
_TEMPLATE = re.compile(r"(^|/)templates/")
_EXAMPLE = re.compile(r"(^|/)(_examples|catalog-examples|fixtures)/")
# A file a message names, such as the two files of a file cycle: `'order.py'`.
_NAMED_FILE = re.compile(r"'([\w.\-/]+\.(?:py|ts|tsx|js|jsx|java))'")


class RepositoryScan:
    """Every rule hit the graph keeps on this repository's code, each with the files it lands in: the node's own file,
    and the files its message names inside the node's folder."""

    def __init__(self) -> None:
        graph = Graph()
        graph.load_files(str(_REPO), [graph.practice_of(CleanEngineering).key], _SCANNED)
        self.hits: list[tuple[str, list[str]]] = []
        for node in graph.practice_of(CleanEngineering).in_graph.nodes():
            for slug in node.rules.failed_slugs:
                self.hits.append((slug, self._files_of(node)))

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
