"""DDD graphQuery rules — CodeQL-appropriate subset.

Skipped (not CodeQL): ubiquitous-language-everywhere, read-all-source-context-in-full,
do-not-invent-concepts, bc-by-lifecycle-not-ui-themes, vendor-not-implementation,
context-tree-bc-aggregate-concept, building-blocks-fidelity-requires-tactical-stereotype,
one-pattern-per-building-block, architectural-granularity-decided — maps, process, or
prose. no-orphaned-objects is a connector (subject class vs mentions in the whole DB).
"""

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "harness", "tools", "actions"):
    _p = str(_REPO_ROOT / _cat)
    if _p not in sys.path:
        sys.path.insert(0, _p)

from expects import equal, expect
from mamba import description, it

_GQS = _REPO_ROOT / "harness" / "knowledge_graph" / "model" / "graph_query_spec.py"
_spec = importlib.util.spec_from_file_location("graph_query_spec", _GQS)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
assert_pack_hits = _mod.assert_pack_hits

_PACK = Path(__file__).resolve().parent
_EXAMPLES = Path(__file__).resolve().parents[2] / "examples"

_RULES = {
    "flaccid-data-object-no-behavior": "ProductData",
    "screen-interface-not-a-domain-object": "CheckoutScreen",
    "private-method-naming": "_hide",
    "no-orphaned-objects": "LonelyType",
    "domain-concepts-not-technical-names": "CartManager",
    "service-is-homeless": "CheckoutService",
    "repository-is-collection-lifecycle": "NoteRepository",
    "load-with-identity-in-hand": "load",
}


with description("DDD graphQuery rules"):
    with it("should hit each CodeQL-appropriate rule example in one batch"):
        misses = assert_pack_hits(_PACK, _EXAMPLES, "python", _RULES)
        expect(misses).to(equal([]))
