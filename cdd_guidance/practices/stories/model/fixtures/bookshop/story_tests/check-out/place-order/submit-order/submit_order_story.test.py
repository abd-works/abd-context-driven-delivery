from __future__ import annotations

from story_test import and_, but_, given, scenario, story, then, when

# Epic: Check Out
# Sub-epic: Place Order
# Map: ../../../../.context/story-map.md#s-customer----submit-order
# Model: ../../../../.context/domain-model.md

# Story: Submit Order
# Actor: Customer
with story("Submit Order"):
    with scenario("Submit a cart with one book"):
        with given("the Customer has [Cart](../../../../.context/domain-model.md#cart-aggregate-root-entity) cart with Tiny Tales"):
            pass
        with when("the Customer submits the [Order](../../../../.context/domain-model.md#order-aggregate-root-entity)"):
            # Order.submit(cart)
            #   -> Cart.total
            #   <- Order
            pass
        with then("the Bookshop keeps [Order](../../../../.context/domain-model.md#order-aggregate-root-entity) order 1001 with status submitted"):
            pass
        with and_("the Order total is 5"):
            pass
    with scenario("Refuse an empty cart"):
        with given("the Customer has [Cart](../../../../.context/domain-model.md#cart-aggregate-root-entity) empty cart"):
            pass
        with when("the Customer submits the [Order](../../../../.context/domain-model.md#order-aggregate-root-entity)"):
            pass
        with then("the Bookshop refuses with \"the cart is empty\""):
            pass
        with but_("no [Order](../../../../.context/domain-model.md#order-aggregate-root-entity) is kept"):
            pass
