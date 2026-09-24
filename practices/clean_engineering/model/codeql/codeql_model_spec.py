"""Predicate and rule queries against examples/ failing assets — one CodeQL batch."""

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

from harness.knowledge_graph.model.graph_query_spec import assert_pack_hits

_PACK = Path(__file__).resolve().parent
_EXAMPLES = Path(__file__).resolve().parents[2] / "examples"

_RULES = {
    "keep-classes-single-responsibility": "CartManager",
    "keep-operations-small-focused": "huge",
    "limit-operation-parameters": "place",
    "avoid-vague-parameter-names": "place_order",
    "simplify-control-flow": "checkout",
    "never-swallow-exceptions": "load_cart",
    "use-exceptions-properly": "load_cart",
    "use-explicit-dependencies": "Cart",
    "use-property-not-accessor": "Cart",
    "prefer-class-operations": "_extended_price",
    "prefer-instance-operations": "is_noun",
    "hide-inner-details": "total",
    "low-coupling": "total",
    "shape-classes-around-resources": "PaymentService",
    "put-logic-on-the-owning-resource": "validate_last_transaction",
    "use-typed-signatures": "checkout",
    "provide-meaningful-context": "split_items",
    "deep-module": "classes publicly",
    "one-way-deps": "alpha",
    "extensions-live-with-the-domain": "GraphEpic",
    "layer-separation": "subtotal",
    "missing-module-context": "OrphanModule",
    "language-modules-one-section": "LanguageSplit",
    "public-seam-only": "Internal design",
    "modules-not-model-blocks": "Live instance",
}


with description("Clean Engineering graphQuery rules"):
    with it("should hit each rule example in one batch"):
        misses = assert_pack_hits(_PACK, _EXAMPLES, "python", _RULES)
        expect(misses).to(equal([]))
