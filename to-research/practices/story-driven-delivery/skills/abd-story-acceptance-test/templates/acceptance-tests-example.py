"""
Place New Order Tests

Tests for stories in the 'Place New Order' sub-epic, driven by
abd-story-specification/reference/examples.md (Manage Customer Orders domain).

Stories / scenarios covered:
- Customer places and tracks a new order (plain scenario, multiple When/Then beats)
- Applying a discount code reduces the order total (scenario outline — parametrized)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import List

import pytest

# =============================================================================
# DOMAIN STUBS — replace with project types during GREEN; keep tests RED until then
# =============================================================================


@dataclass
class Customer:
    name: str
    account_active: bool = True
    orders: List["Order"] = field(default_factory=list)


@dataclass
class Cart:
    customer: Customer
    lines: List[tuple[str, Decimal]] = field(default_factory=list)

    def add_items(self, items: List[tuple[str, Decimal]]) -> None:
        self.lines.extend(items)

    def submit(self) -> "Order":
        raise NotImplementedError("GREEN: create Order from cart")


@dataclass
class Order:
    customer: Customer
    tracking_number: str | None = None
    status: str = "Processing"

    def dispatch(self) -> None:
        raise NotImplementedError("GREEN: mark order Shipped and notify customer")


@dataclass
class DiscountResult:
    order_total: Decimal
    discount_description: str


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================


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


# =============================================================================
# FIXTURES — Background shared by 3+ scenarios (Given/And only)
# =============================================================================


@pytest.fixture
def given_warehouse_and_customer() -> Customer:
    given_warehouse_central_hub_with_standard_inventory()
    return given_customer_with_active_account("Jane Doe")


# =============================================================================
# STORY: Customer places and tracks a new order
# (spec: plain scenario — multiple When/Then beats)
# =============================================================================


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


# =============================================================================
# STORY: Applying a discount code reduces the order total
# (spec: scenario outline — Examples: DiscountCode + CartAndResult)
# =============================================================================


class TestApplyDiscountCodeReducesOrderTotal:
    """Applying a discount code reduces the order total."""

    @pytest.mark.parametrize(
        "scenario,code,discount_description,original_total,discounted_total",
        [
            ("Percentage off", "SAVE20", "20% off", "50.00", "40.00"),
            ("Fixed amount off", "FLAT10", "$10.00 off", "50.00", "40.00"),
        ],
        ids=["percentage_off", "fixed_amount_off"],
    )
    def test_discount_reduces_order_total(
        self,
        given_warehouse_and_customer: Customer,
        scenario: str,
        code: str,
        discount_description: str,
        original_total: str,
        discounted_total: str,
    ) -> None:
        """
        SCENARIO OUTLINE: Applying a discount code reduces the order total
        GIVEN: a Customer {customer_name} with an active account
        AND: a Cart containing items totalling {original_total}
        WHEN: the Customer applies Discount Code {code}
        THEN: the Order Total is {discounted_total}
        AND: the Discount line shows {discount_description}
        """
        customer = given_warehouse_and_customer
        cart = given_cart_with_items(
            customer, [("Sample product", Decimal(original_total))]
        )

        result = when_customer_applies_discount_code(cart, code)

        then_order_total_is(result, discounted_total)
        then_discount_line_shows(result, discount_description)
