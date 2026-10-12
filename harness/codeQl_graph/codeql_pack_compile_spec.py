"""Compile and evaluate every graph query the explorer runs (practices + pattern overlay)."""

import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from expects import be_above, contain, equal, expect
from mamba import before, context, description, it

from graph import CodeQLGraph, QueryFailure, normalize_overlay

_ROOT = _HERE
_SAMPLE = _ROOT / "examples" / "input"
_PRACTICES = ["clean_engineering", "stories", "ddd", "bdd", "ux"]
_OVERLAY = normalize_overlay("lern_domain_driven")
_KINDS = ("nodes", "edges", "rules")


def _explorer_query_paths(graph: CodeQLGraph) -> list[str]:
    paths: list[str] = []
    for practice in _PRACTICES:
        for kind in _KINDS:
            paths.extend(graph.query_files(practice, kind))
    return sorted({str(Path(path).resolve()) for path in paths})


def _sample_working_copy() -> Path:
    return _SAMPLE / ".codeql" / "clean_engineering" / "typescript-working-copy"


def _bind_explorer_graph(graph: CodeQLGraph) -> None:
    roots = {name: str(_SAMPLE) for name in _PRACTICES}
    graph._bind(str(_ROOT), roots, database=str(_SAMPLE))
    graph.overlays = [_OVERLAY]
    graph.use_query_server = False


with description("CodeQL pack compile gate"):
    with context("with lern_domain_driven on the account-credentials sample"):
        with before.all:
            if shutil.which("codeql") is None:
                raise AssertionError("codeql is not on PATH; install CodeQL to run the pack compile gate")
            self.graph = CodeQLGraph()
            _bind_explorer_graph(self.graph)
            working = _sample_working_copy()
            if not self.graph._database_ready(working):
                roots = {name: str(_SAMPLE) for name in _PRACTICES}
                self.graph.create_database(str(_ROOT), roots, database=str(_SAMPLE))
            self.database = working
            self.queries = _explorer_query_paths(self.graph)

        with it("should list overlay story tier queries in the explorer set"):
            names = {Path(path).name for path in self.queries}
            expect(names).to(contain("domain-spec.ql"))
            expect(names).to(contain("story-shared.ql"))
            expect(len(self.queries)).to(be_above(80))

        with it("should compile and evaluate every node, edge, and rule query"):
            try:
                decoded = self.graph.run_queries(self.queries, self.database, reuse=False)
            except QueryFailure as error:
                raise AssertionError(str(error)) from error
            expect(len(decoded)).to(equal(len(self.queries)))
