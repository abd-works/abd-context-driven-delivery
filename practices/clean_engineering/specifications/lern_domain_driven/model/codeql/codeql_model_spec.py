"""LERN graphQuery rules — CodeQL-appropriate subset of the architecture scanners."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[6]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from harness.knowledge_graph.model.graph_query_spec import assert_pack_hits

_PACK = Path(__file__).resolve().parent
_EXAMPLES = Path(__file__).resolve().parents[2] / "examples" / "codeql"

_RULES = {
    "organize-by-domain-module": "*-client.tsx",
    "share-domain-logic": "Zod schema definition",
    "maintain-layer-purity": "forbidden framework import",
    "use-ubiquitous-language": "technical suffix",
    "cross-layer-method-naming": "fetchRecipients",
    "preserve-arg-names-across-layers": "does not preserve core name",
    "property-casing-transform": "snake_case",
    "consistent-view-naming": "RecipientPage",
    "delegate-routes-to-domain-server": "repository directly",
    "ensure-type-safe-routes": "as any",
    "standard-mutation-response": "success/message/ok",
    "implement-domain-entities-correctly": "no behaviour",
    "implement-full-interfaces": "not implemented",
    "use-valid-package-names": "placeholder npm scope",
    "include-all-external-dependencies": "lodash",
    "test-story-driven": "story-driven tier suffix",
    "scaffold-test-scripts": "playwright.config.ts",
    "use-thorough-e2e-tests": "Blanket delete",
    "one-json-store-per-aggregate": "db.json",
    "repository-owns-aggregate-lifecycle": "missing load",
    "ask-cross-aggregate-sync": "more than one aggregate",
}


with description("LERN graphQuery rules"):
    with it("should hit each CodeQL-appropriate rule example in one batch"):
        misses = assert_pack_hits(_PACK, _EXAMPLES, "javascript", _RULES)
        expect(misses).to(equal([]))
