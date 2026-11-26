from __future__ import annotations

from expects import equal, expect, raise_error

from story_test import and_, given, scenario, story, then, when
from src.bookshop.order import OrderNotPaid, OrderRepository
from story_tests.fulfil_order.examples.order_examples import paid_order, unpaid_order

# Epic: Fulfil Order
# Map: ../../../.context/story-map.md#s-shop-clerk----pack-order
# Model: ../../../.context/domain-model.md

# Story: Pack Order
# Actor: Shop Clerk
with story("Pack Order"):
    with scenario("Pack a paid order"):
        with given("the Bookshop keeps [Order](../../../.context/domain-model.md#order-aggregate-root-entity) paid order"):
            orders = OrderRepository()
            orders.create(paid_order())
        with when("the Shop Clerk packs the Order"):
            # Order.pack()
            orders.load("1001").pack()
        with then("the [Order](../../../.context/domain-model.md#order-aggregate-root-entity) paid order has status packed"):
            expect(orders.load("1001").status).to(equal("packed"))
    with scenario("Refuse to pack an unpaid order"):
        with given("the Bookshop keeps [Order](../../../.context/domain-model.md#order-aggregate-root-entity) unpaid order"):
            orders = OrderRepository()
            orders.create(unpaid_order())
        with when("the Shop Clerk packs the Order"):
            packing = lambda: orders.load("1002").pack()
        with then("the Bookshop refuses with \"order 1002 is not paid\""):
            expect(packing).to(raise_error(OrderNotPaid, "order 1002 is not paid"))
        with and_("the [Order](../../../.context/domain-model.md#order-aggregate-root-entity) unpaid order keeps status submitted"):
            expect(orders.load("1002").status).to(equal("submitted"))
