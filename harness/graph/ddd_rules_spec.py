"""DDD tactical graph rules — python .examples pairs."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parents[1]
for path in (_HERE, _REPO):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from mamba import context, description, it

from harness.graph.ddd_rule_eval_harness import assert_ddd_example_pair

with description("DDD tactical rules (python .examples)"):
    with context("building-blocks-fidelity-requires-tactical-stereotype"):
        with it("should flag Plan without stereotype and accept PlanEntity"):
            assert_ddd_example_pair(
                "building-blocks-fidelity-requires-tactical-stereotype",
                "Plan",
                clean_class="PlanEntity",
            )

    with context("domain-concepts-not-technical-names"):
        with it("should flag CartManager and accept Cart"):
            assert_ddd_example_pair(
                "domain-concepts-not-technical-names",
                "CartManager",
                clean_class="Cart",
            )

    with context("flaccid-data-object-no-behavior"):
        with it("should flag field-only Cart and accept Product with behavior"):
            assert_ddd_example_pair(
                "flaccid-data-object-no-behavior",
                "Cart",
                clean_class="Product",
            )

    with context("private-method-naming"):
        with it("should flag cross-type private access on Other"):
            assert_ddd_example_pair(
                "private-method-naming",
                "Other",
                clean_class="Cart",
            )

    with context("service-is-homeless"):
        with it("should flag CheckoutService and accept behavior on Cart"):
            assert_ddd_example_pair(
                "service-is-homeless",
                "CheckoutService",
                clean_class="Cart",
                node_type="DomainService",
            )

    with context("repository-is-collection-lifecycle"):
        with it("should flag persist-only NoteRepository"):
            assert_ddd_example_pair("repository-is-collection-lifecycle", "NoteRepository", node_type="Repository")

    with context("load-with-identity-in-hand"):
        with it("should flag load without identity parameter"):
            assert_ddd_example_pair("load-with-identity-in-hand", "CustomerRepository", node_type="Repository")

    with context("no-orphaned-objects"):
        with it("should flag LonelyType and accept related Cart"):
            assert_ddd_example_pair("no-orphaned-objects", "LonelyType", clean_class="Cart")

    with context("screen-interface-not-a-domain-object"):
        with it("should flag SelectSim and accept Checkout"):
            assert_ddd_example_pair(
                "screen-interface-not-a-domain-object",
                "SelectSim",
                clean_class="Checkout",
            )
