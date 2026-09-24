"""keep-classes-single-responsibility clusters named jobs, not leftover nouns."""

from pathlib import Path
import sys

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import description, it

from practices.clean_engineering.model.responsibilities import Responsibilities


class ResponsibilityHits:
    def from_operations(self, class_name: str, operations: dict[str, list[str]]) -> list[dict]:
        hits = []
        for operation, tokens in operations.items():
            for token in tokens:
                hits.append(
                    {"name": class_name, "contributor": operation, "message": token}
                )
        return hits


_CART = {
    "add": ["add"],
    "remove": ["remove"],
    "clear": ["clear"],
    "checkout": ["checkout"],
    "apply_tax": ["apply", "tax"],
    "apply_discount": ["apply", "discount"],
    "write_audit": ["write", "audit"],
    "send_email": ["send", "email"],
    "render": ["render"],
    "persist": ["persist"],
    "load": ["load"],
}

_GRAPH_RULE = {
    "validate": ["validate"],
    "evaluate": ["evaluate"],
    "load_graph_query": ["load", "graph", "query"],
    "hits_from_query": ["hits", "from", "query"],
    "query_pack": ["query", "pack"],
    "pack_rules_query": ["pack", "rules", "query"],
    "graphQuery": ["graph", "query"],
    "inherits_to_children": ["inherits", "to", "children"],
}


with description("hits_for_keep_classes"):
    with it("should flag a class whose public operations name four jobs"):
        flagged = Responsibilities().hits_for_keep_classes(ResponsibilityHits().from_operations("CartManager", _CART))
        expect(len(flagged) > 0).to(equal(True))
        expect("CartManager" in flagged[0]["message"]).to(equal(True))

    with it("should not flag a graph Rule whose operations share query language"):
        flagged = Responsibilities().hits_for_keep_classes(ResponsibilityHits().from_operations("GraphRule", _GRAPH_RULE))
        expect(flagged).to(equal([]))
