"""UX graphQuery rules — CodeQL-appropriate subset.

Skipped (not CodeQL): ia-named-regions-only, tab-states-are-separate-screens,
screen-story-budget, brand-is-opt-in, shell-from-template — markdown/HTML map
structure. screen-names-use-domain-terms is a connector (title vs classes in the DB).
"""

import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))
for _cat in ("practices", "tools", "actions"):
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
    "story-domain-js-imported": "stub adapter",
    "key-interactions-wired": "data-goto",
    "screen-names-use-domain-terms": "CheckoutScreen",
}


with description("UX graphQuery rules"):
    with it("should hit each CodeQL-appropriate rule example in one batch"):
        misses = assert_pack_hits(_PACK, _EXAMPLES, "javascript", _RULES)
        expect(misses).to(equal([]))
