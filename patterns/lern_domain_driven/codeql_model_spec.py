"""LERN graphQuery rules — CodeQL-appropriate subset of the architecture scanners."""

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions", "patterns"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

from harness.knowledge_graph.model.graph_query_spec import assert_pack_hits

_LERN = Path(__file__).resolve().parent
_EXAMPLES = _LERN / "examples" / "codeql"

_PRACTICES = _LERN / "practices"
_CLEAN_ENGINEERING_PACK = _PRACTICES / "clean_engineering" / "model" / "typescript" / "codeql"
_DDD_PACK = _PRACTICES / "ddd" / "model" / "typescript" / "codeql"
_STORIES_PACK = _PRACTICES / "stories" / "model" / "typescript" / "codeql"

_RULES_BY_PACK = {
    _CLEAN_ENGINEERING_PACK: {
        "epic-package-screens-only": "belongs under src",
        "domain-core-file-matches-folder-slug": "kebab-case",
        "node-tier-uses-node-suffix": "-server.ts",
        "client-subtypes-domain-hosts-browser-logic": "subtypes Transfers",
        "node-decides-next-page": "node class decides",
        "router-asks-the-node": "repository directly",
        "views-render-only": "only renders",
        "share-domain-logic": "Zod schema definition",
        "maintain-layer-purity": "forbidden framework import",
        "cross-layer-method-naming": "fetchRecipients",
        "preserve-arg-names-across-layers": "does not preserve core name",
        "property-casing-transform": "snake_case",
        "consistent-view-naming": "RecipientPage",
        "ensure-type-safe-routes": "as any",
        "standard-mutation-response": "success/message/ok",
        "implement-full-interfaces": "not implemented",
        "use-valid-package-names": "placeholder npm scope",
        "include-all-external-dependencies": "lodash",
    },
    _DDD_PACK: {
        "use-ubiquitous-language": "technical suffix",
        "implement-domain-entities-correctly": "no behaviour",
        "one-json-store-per-aggregate": "db.json",
        "repository-owns-aggregate-lifecycle": "missing load",
    },
    _STORIES_PACK: {
        "test-story-driven": "story-driven tier suffix",
        "scaffold-test-scripts": "playwright.config.ts",
        "use-thorough-e2e-tests": "Blanket delete",
        "ask-cross-aggregate-sync": "more than one aggregate",
    },
}


with description("LERN graphQuery rules"):
    with it("should hit each CodeQL-appropriate rule example in its practice pack"):
        misses: list[str] = []
        for pack, rules in _RULES_BY_PACK.items():
            misses.extend(assert_pack_hits(pack, _EXAMPLES, "javascript", rules))
        expect(misses).to(equal([]))
