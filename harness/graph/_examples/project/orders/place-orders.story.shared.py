"""Place Orders: the shared scenarios the Python tiers replay. Map: .context/story-map.md."""

from orders.orders_examples import ALICES_ORDER, EMPTY_ORDER

shared_stories = SharedStories("Place Orders")


@shared_stories.scenario("Place Order", "Place an order for two pets")
def _(s):
    @s.given("Alice has two pets in her basket")
    def _(world):
        world.order = world.Order(ALICES_ORDER.shopper)

    @s.when("Alice places her order")
    def _(world):
        world.order.place("cat", "dog", "", "", "")

    @s.then("the order is confirmed")
    def _(world):
        assert world.order.confirm()


@shared_stories.scenario("Place Order", "Refuse an empty order")
def _(s):
    @s.when("Bob places an order with no pets")
    def _(world):
        world.order = world.Order(EMPTY_ORDER.shopper)

    @s.then("nothing is confirmed")
    def _(world):
        assert world.order.total == 0
