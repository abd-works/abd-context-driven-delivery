"""Query-server batching avoids compiling every rule in one JVM compile."""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import context, description, it

from harness.codeQl_graph.graph import (
    _chunk_queries,
    _query_server_batch_failure,
    _query_server_memory_failure,
)


with description("CodeQL query-server batching"):

    with context("batch helpers"):

        with it("chunks queries when batch size is smaller than the list"):
            queries = [f"q{i}.ql" for i in range(10)]
            expect(_chunk_queries(queries, 3)).to(equal([queries[0:3], queries[3:6], queries[6:9], queries[9:10]]))

        with it("keeps one chunk when batch size is zero or covers the list"):
            queries = ["a.ql", "b.ql"]
            expect(_chunk_queries(queries, 0)).to(equal([queries]))
            expect(_chunk_queries(queries, 25)).to(equal([queries]))

        with it("detects JVM heap failures for batch fallback"):
            detail = "evaluation/runQueries failed: Internal error.\njava.lang.OutOfMemoryError: Java heap space"
            expect(_query_server_memory_failure(detail)).to(equal(True))
            expect(_query_server_batch_failure(detail)).to(equal(True))

        with it("does not treat dbscheme mismatch as a batch failure"):
            detail = "no upgrade path from old dbscheme"
            expect(_query_server_batch_failure(detail)).to(equal(False))
