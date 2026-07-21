"""
# @toolset-manifest python -m tools manifest contexts.clean_engineering.clean_engineering:CleanEngineering
"""
# ============================================================================
# phone_cart.py
#
# Domain area   : phone products and accessories cart
# Responsibilities: hold phone products and accessories, compute totals,
#                   place a purchase order
# ============================================================================

# stdlib
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


# ============================================================================
# DOMAIN CONSTANTS
# ============================================================================

TAX_RATE = 0.10                  # sales tax applied to all orders
MAX_LOYALTY_DISCOUNT = 0.15      # loyalty programme cap for repeat customers
LOYALTY_PURCHASE_THRESHOLD = 750 # cumulative spend that unlocks loyalty pricing


# ============================================================================
# DOMAIN EXCEPTIONS
# ============================================================================

class CartError(Exception):
    """Base exception for phone cart domain failures."""


class EmptyCartError(CartError):
    """Raised when place_order() is called on an empty cart."""


class InvalidQuantityError(CartError):
    """Raised when a line item is added with a non-positive quantity."""


class ProductNotInCartError(CartError):
    """Raised when removing or updating a product that is not in the cart."""


class OrderError(Exception):
    """Base exception for purchase order domain failures."""


class OrderAlreadyConfirmedError(OrderError):
    """Raised when confirm() is called on an already-confirmed order."""


class CheckoutError(CartError):
    """Base exception for checkout domain failures."""


class UnsupportedPaymentMethodError(CheckoutError):
    """Raised when a payment method is not accepted at checkout."""


# ============================================================================
# DOMAIN ENTITY: ProductCategory
# ============================================================================

class ProductCategory(Enum):
    PHONE = "phone"
    ACCESSORY = "accessory"


# ============================================================================
# DOMAIN ENTITY: PaymentMethod
# ============================================================================

class PaymentMethod(Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"


# ============================================================================
# DOMAIN ENTITY: Product
#
# A Product owns its own price. No other class stores a copy of it.
# ============================================================================

@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    brand: str
    category: ProductCategory
    price: float


# ============================================================================
# DOMAIN ENTITY: LineItem
#
# A LineItem is a chosen quantity of a Product.
# It derives its extended price from the Product -- no stored duplicate.
# ============================================================================

class LineItem:
    """A quantity of a specific Product chosen for a cart."""

    def __init__(self, product: Product, qty: int) -> None:
        if qty < 1:
            raise InvalidQuantityError(
                f"qty for '{product.sku}' must be >= 1, got {qty}"
            )
        self._product = product
        self._qty = qty

    @property
    def product(self) -> Product:
        return self._product

    @property
    def qty(self) -> int:
        return self._qty

    @property
    def extended_price(self) -> float:
        """Price comes from the Product -- not a stored copy."""
        return round(self._product.price * self._qty, 2)

    def with_qty(self, qty: int) -> LineItem:
        """Return a new LineItem with updated quantity."""
        return LineItem(product=self._product, qty=qty)


# ============================================================================
# DOMAIN ENTITY: Cart
#
# A Cart owns its items and all pricing logic for those items.
# It knows whether it is empty, what it costs, and how to become an Order.
# Collaborators injected via constructor: none -- Cart is a pure domain object.
# ============================================================================

class Cart:
    """A shopping cart for phone products and accessories."""

    def __init__(self, customer: Customer) -> None:
        self._customer = customer
        self._items: list[LineItem] = []

    # ------------------------------------------------------------------
    # Properties -- what this Cart IS
    # ------------------------------------------------------------------

    @property
    def customer(self) -> Customer:
        return self._customer

    @property
    def items(self) -> tuple[LineItem, ...]:
        return tuple(self._items)

    @property
    def is_empty(self) -> bool:
        return len(self._items) == 0

    @property
    def item_count(self) -> int:
        return sum(line_item.qty for line_item in self._items)

    @property
    def subtotal(self) -> float:
        return round(sum(line_item.extended_price for line_item in self._items), 2)

    # ------------------------------------------------------------------
    # Domain responsibilities -- what this Cart CAN DO
    # ------------------------------------------------------------------

    def add(self, product: Product, qty: int) -> None:
        """Add a quantity of a product. Raises InvalidQuantityError if qty < 1."""
        existing = self._find_item(product.sku)
        if existing is not None:
            self._replace_item(product.sku, existing.with_qty(existing.qty + qty))
        else:
            self._items.append(LineItem(product=product, qty=qty))

    def remove(self, sku: str) -> None:
        """Remove all line items for the given SKU. Raises ProductNotInCartError if absent."""
        if not self._contains(sku):
            raise ProductNotInCartError(f"Product '{sku}' is not in the cart.")
        self._items = [i for i in self._items if i.product.sku != sku]

    def update_quantity(self, sku: str, qty: int) -> None:
        """Change the quantity of an existing cart line. Raises ProductNotInCartError if absent."""
        existing = self._find_item(sku)
        if existing is None:
            raise ProductNotInCartError(f"Product '{sku}' is not in the cart.")
        self._replace_item(sku, existing.with_qty(qty))

    def place_order(self, payment_method: PaymentMethod) -> Order:
        """Convert this cart into a Purchase Order with the chosen payment method, or raise EmptyCartError."""
        if self.is_empty:
            raise EmptyCartError("Cannot place an order from an empty cart.")
        return Order(customer=self._customer, items=self.items, payment_method=payment_method)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _find_item(self, sku: str) -> LineItem | None:
        return next((i for i in self._items if i.product.sku == sku), None)

    def _contains(self, sku: str) -> bool:
        return self._find_item(sku) is not None

    def _replace_item(self, sku: str, replacement: LineItem) -> None:
        self._items = [
            replacement if i.product.sku == sku else i
            for i in self._items
        ]


# ============================================================================
# DOMAIN ENTITY: Order
#
# An Order owns its pricing, tax, and confirmation lifecycle.
# It knows its own total; no service calculates this on its behalf.
# Collaborators injected via constructor: none -- Order is a pure domain object.
# ============================================================================

class Order:
    """A purchase order for phone products and accessories."""

    def __init__(self, customer: Customer, items: tuple[LineItem, ...], payment_method: PaymentMethod) -> None:
        self._customer = customer
        self._items = items
        self._payment_method = payment_method
        self._confirmed = False

    # ------------------------------------------------------------------
    # Properties -- what this Order IS
    # ------------------------------------------------------------------

    @property
    def customer(self) -> Customer:
        return self._customer

    @property
    def items(self) -> tuple[LineItem, ...]:
        return self._items

    @property
    def subtotal(self) -> float:
        return round(sum(line_item.extended_price for line_item in self._items), 2)

    @property
    def tax(self) -> float:
        return round(self.subtotal * TAX_RATE, 2)

    @property
    def total(self) -> float:
        pre_discount = self.subtotal + self.tax
        return round(self._apply_loyalty_discount(pre_discount), 2)

    @property
    def payment_method(self) -> PaymentMethod:
        return self._payment_method

    @property
    def is_confirmed(self) -> bool:
        return self._confirmed

    # ------------------------------------------------------------------
    # Domain responsibilities -- what this Order CAN DO
    # ------------------------------------------------------------------

    def confirm(self) -> None:
        """Mark this order as confirmed. Raises OrderAlreadyConfirmedError if already done."""
        if self._confirmed:
            raise OrderAlreadyConfirmedError("Order is already confirmed.")
        self._confirmed = True

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_loyalty_discount(self, amount: float) -> float:
        if self._customer.lifetime_spend < LOYALTY_PURCHASE_THRESHOLD:
            return amount
        discount_rate = min(self._customer.loyalty_rate, MAX_LOYALTY_DISCOUNT)
        return amount * (1 - discount_rate)


# ============================================================================
# DOMAIN ENTITY: Customer
# ============================================================================

@dataclass
class Customer:
    customer_id: str
    email: str
    lifetime_spend: float = 0.0
    loyalty_rate: float = 0.0
