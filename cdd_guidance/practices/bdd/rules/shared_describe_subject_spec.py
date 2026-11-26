"""shared-describe-subject graph rule."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from mamba import before, context, description, it

from cdd_guidance.practices.bdd.rules.rule_examples import EXAMPLE_SOURCES, assert_bdd_example_pair, assert_bdd_source_pair, spec_fixture

_FAULT, _CLEAN = EXAMPLE_SOURCES["shared-describe-subject"]

_SCRIPT_FAULT = """
describe("a bare agentic toolset registered for deploy", () => {});

describe("a bare agentic toolset with mcp-published operations registered for deploy", () => {});
"""

_SCRIPT_CLEAN = """
describe("a bare agentic toolset registered for deploy", () => {
  describe("with no mcp-published operations", () => {});
  describe("with mcp-published operations", () => {});
});
"""


with description("shared-describe-subject rule"):
    # The first fixture loads the practices' guidance and readers; it is read here once, so no example pays for it.
    with before.all:
        spec_fixture(_CLEAN)

    with context("on a spec source pair"):
        with it("should flag repeated top-level describe prefixes"):
            assert_bdd_example_pair("shared-describe-subject")

    with context("on a spec source pair whose describes are written in single quotes"):
        with it("should flag repeated top-level describe prefixes"):
            assert_bdd_source_pair("shared-describe-subject", _FAULT.replace('"', "'"), _CLEAN.replace('"', "'"))

    with context("on a typescript spec source pair"):
        with it("should flag repeated top-level describe prefixes"):
            assert_bdd_source_pair("shared-describe-subject", _SCRIPT_FAULT, _SCRIPT_CLEAN, filename="widget.spec.ts")
