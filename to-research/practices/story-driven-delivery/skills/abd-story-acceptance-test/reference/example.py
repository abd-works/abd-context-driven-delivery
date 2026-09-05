class TestCustomerPlacesAndTracksNewOrder:
    def test_order_confirmed_tracked_and_shipped(
        self, given_warehouse_and_customer: Customer
    ) -> None:

        customer = given_warehouse_and_customer
        cart = given_cart_with_items(
            customer, [("Kibble 5kg", Decimal("24.99"))]
        )
        order = when_customer_adds_items_and_submits_order(cart)
        then_order_is_confirmed_with_tracking_number(order)
        then_order_status_is(order, "Processing")

        active_orders = when_customer_views_active_orders(customer)
        then_order_is_displayed_among_active_orders(active_orders, order)
        then_order_status_is(order, "Processing")

        when_order_is_dispatched(order)
        then_customer_receives_shipment_notification(customer, order)
        then_order_status_is(order, "Shipped")


def given_warehouse_central_hub_with_standard_inventory() -> None:
    """Background: Warehouse 'Central Hub' with Inventory for standard products."""
    raise NotImplementedError("GREEN: seed warehouse inventory")
def given_customer_with_active_account(name: str = "Jane Doe") -> Customer:
    """Background / Given: Customer with an active account."""
    return Customer(name=name, account_active=True)
def given_cart_with_items(customer: Customer, items: List[tuple[str, Decimal]]) -> Cart:
    """Given: cart containing items (product label, line total)."""
    cart = Cart(customer=customer)
    cart.add_items(items)
    return cart
def when_customer_adds_items_and_submits_order(cart: Cart) -> Order:
    """When: Customer adds items to the cart and submits the order."""
    return cart.submit()
def when_customer_views_active_orders(customer: Customer) -> List[Order]:
    """When: Customer views active orders for their account."""
    raise NotImplementedError("GREEN: return active orders for customer")
def when_order_is_dispatched(order: Order) -> None:
    """When: the order is dispatched."""
    order.dispatch()
def when_customer_applies_discount_code(cart: Cart, code: str) -> DiscountResult:
    """When: Customer applies Discount Code."""
    raise NotImplementedError(f"GREEN: apply discount code {code!r}")
def then_order_is_confirmed_with_tracking_number(order: Order) -> None:
    """Then: order is confirmed with a tracking number."""
    assert order.tracking_number is not None
def then_order_is_displayed_among_active_orders(
    orders: List[Order], expected: Order
) -> None:
    """Then: that order is displayed along with any other active orders."""
    assert expected in orders
def then_order_status_is(order: Order, status: str) -> None:
    """Then / And: status for that order is displayed."""
    assert order.status == status
def then_customer_receives_shipment_notification(customer: Customer, order: Order) -> None:
    """Then: Customer receives a shipment notification."""
    raise NotImplementedError("GREEN: assert notification sent")
def then_order_total_is(result: DiscountResult, expected: str) -> None:
    """Then: Order Total matches expected amount."""
    assert result.order_total == Decimal(expected)
def then_discount_line_shows(result: DiscountResult, description: str) -> None:
    """And: Discount line shows expected description."""
    assert result.discount_description == description
@pytest.fixture
def given_warehouse_and_customer() -> Customer:
    given_warehouse_central_hub_with_standard_inventory()
    return given_customer_with_active_account("Jane Doe")

