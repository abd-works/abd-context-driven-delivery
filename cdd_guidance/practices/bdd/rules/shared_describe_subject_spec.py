"""shared-describe-subject graph rule."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from mamba import before, context, description, it

from cdd_guidance.practices.bdd.rules.rule_examples import assert_bdd_source_pair, spec_fixture

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
    # The first fixture loads the practices' guidance and readers; it is read here once, so no example pays for it.
    with before.all:
        spec_fixture(_CLEAN)

    with context("on a spec source pair"):
        with it("should flag repeated top-level describe prefixes"):
            assert_bdd_source_pair("shared-describe-subject", _FAULT, _CLEAN)
