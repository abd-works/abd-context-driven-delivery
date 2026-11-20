from __future__ import annotations

from story_test import and_, given, scenario, story, then, when

# Epic: Check Out
# Sub-epic: Place Order
# Map: ../../../../.context/story-map.md#ssystem-payment-provider----authorize-payment
# Model: ../../../../.context/domain-model.md

# Story: Authorize Payment
# Actor: Payment Provider
with story("Authorize Payment"):
    with scenario("Authorize a payment for the order total"):
        with given("the Bookshop keeps [Order](../../../../.context/domain-model.md#order-aggregate-root-entity) order 1001 with total 5"):
            pass
        with when("the Payment Provider receives a [Payment](../../../../.context/domain-model.md#payment-value-object) request of 5 for order 1001"):
            pass
        with then("the Payment Provider answers authorized"):
            pass
        with and_("the [Order](../../../../.context/domain-model.md#order-aggregate-root-entity) order 1001 holds a [Payment](../../../../.context/domain-model.md#payment-value-object) of 5 with status authorized"):
            pass
    with scenario("Decline a payment over the card limit"):
        with given("the Bookshop keeps [Order](../../../../.context/domain-model.md#order-aggregate-root-entity) order 1002 with total 900"):
            pass
        with when("the Payment Provider receives a [Payment](../../../../.context/domain-model.md#payment-value-object) request of 900 for order 1002"):
            pass
        with then("the Payment Provider answers declined"):
            pass
        with and_("the [Order](../../../../.context/domain-model.md#order-aggregate-root-entity) order 1002 stays unpaid"):
            pass
