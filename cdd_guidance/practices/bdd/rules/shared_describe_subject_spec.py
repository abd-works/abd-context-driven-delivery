"""shared-describe-subject graph rule."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[3]
_GRAPH = _REPO / "harness" / "graph"
for path in (_GRAPH, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from mamba import context, description, it

from bdd_example_harness import assert_bdd_source_pair

_FAULT = """
with description("a bare agentic toolset registered for deploy"):
    pass

with description("a bare agentic toolset with mcp-published operations registered for deploy"):
    pass
"""

_CLEAN = """
with description("a bare agentic toolset registered for deploy"):
    with context("with no mcp-published operations"):
        pass
    with context("with mcp-published operations"):
        pass
"""


with description("shared-describe-subject rule"):
    with context("on a spec source pair"):
        with it("should flag repeated top-level describe prefixes"):
            assert_bdd_source_pair("shared-describe-subject", _FAULT, _CLEAN)
