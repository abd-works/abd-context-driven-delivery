"""Fulfil Order: the shared scenarios the Python tiers replay.

Map: .context/story-map.md#e-fulfil-order. Model: .context/domain-model.md.
"""

from __future__ import annotations

from expects import equal, expect

from src.bookshop.order import OrderRepository
from story_tests.fulfil_order.examples.order_examples import PAID_ORDER, paid_order
from story_tests.shared_stories import SharedStories

shared_stories = SharedStories("Fulfil Order")


@shared_stories.scenario("Mark Order Shipped", "Mark a packed order shipped")
def _(s):
    @s.given("the Bookshop keeps Order paid order, packed")
    def _(world):
        world.orders = OrderRepository()
        world.orders.create(paid_order()).pack()

    @s.when("the Shop Clerk marks the Order shipped")
    def _(world):
        world.order = world.orders.load(PAID_ORDER.number)
        world.order.status = "shipped"

    @s.then("the Order paid order has status shipped")
    def _(world):
        expect(world.orders.load(PAID_ORDER.number).status).to(equal("shipped"))


@shared_stories.scenario("Mark Order Shipped", "Keep an order that is not packed as it is")
def _(s):
    @s.given("the Bookshop keeps Order paid order, submitted")
    def _(world):
        world.orders = OrderRepository()
        world.orders.create(paid_order())

    @s.when("the Shop Clerk lists the orders ready to ship")
    def _(world):
        world.ready = [order for order in [world.orders.load(PAID_ORDER.number)] if order.status == "packed"]

    @s.then("the list holds no Order")
    def _(world):
        expect(world.ready).to(equal([]))
