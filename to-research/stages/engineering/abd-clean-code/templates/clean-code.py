"""
## Instructions (remove this block before committing to production)
##
## This template shows the canonical layout for a clean production Python module.
## Steps:
##   1. Replace <domain_area> with the sub-epic or bounded context name (snake_case).
##   2. Replace each domain class with entities from your story's domain model.
##   3. Replace placeholder method names with domain responsibility verbs.
##   4. Delete this Instructions block.
##   5. Run peer-review against abd-clean-code rules before opening a PR.
##
## Layout:
##   Module docstring  (domain area + responsibilities)
##   Imports           (stdlib -> third-party -> local)
##   DOMAIN CONSTANTS  (named constants, no magic numbers)
##   DOMAIN EXCEPTIONS (named for what went wrong in the domain)
##   DOMAIN ENTITIES   (classes that own both state AND behaviour)
##     __init__        (accept infrastructure deps via injection; no construction inside)
##     properties      (what the object IS / CONTAINS -- computed, not stored raw)
##     public methods  (what the object CAN DO -- domain verbs)
##     _private helps  (implementation details, under 20 lines each)
##
## KEY RULE: domain logic belongs on domain objects, not in services.
## A Cart knows its own subtotal. An Order knows whether it is confirmed.
## A service that accepts a pile of DTOs and does all the work is the
## Anemic Domain Model anti-pattern -- avoid it.
"""
# ============================================================================
# <domain_area>.py
#
# Domain area : <e.g. cart, order, inventory>
# Responsibilities: <list the domain behaviours this module covers>
# ============================================================================

# stdlib
from __future__ import annotations
from dataclasses import dataclass

# third-party  (add as needed)

# local
# from <package>.<module> import <Symbol>

# ============================================================================
# DOMAIN CONSTANTS
# ============================================================================

TAX_RATE = 0.13              # GST/HST applied to all orders
MAX_LOYALTY_DISCOUNT = 0.40  # loyalty programme cap
LOYALTY_THRESHOLD = 1000     # cumulative spend that unlocks loyalty pricing


# ============================================================================
# DOMAIN EXCEPTIONS
# ============================================================================

class CartError(Exception):
    """Base exception for cart domain failures."""


class EmptyCartError(CartError):
    """Raised when an order is placed from an empty cart."""


class InvalidQuantityError(CartError):
    """Raised when a line item is added with a non-positive quantity."""


class OrderError(Exception):
    """Base exception for order domain failures."""


class OrderAlreadyConfirmedError(OrderError):
    """Raised when confirm() is called on an already-confirmed order."""


# ============================================================================
# DOMAIN ENTITY: Product
#
# A Product owns its own price. No other class stores a copy of it.
# ============================================================================

@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price: float


# ============================================================================
# DOMAIN ENTITY: LineItem
#
# A LineItem is a chosen quantity of a Product.
# It gets its price from the Product -- it does not store a duplicate.
# ============================================================================

class LineItem:
    """A quantity of a specific Product chosen for a cart."""

    def __init__(self, product: Product, qty: int) -> None:
        if qty < 1:
            raise InvalidQuantityError(product.sku, qty)
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


# ============================================================================
# DOMAIN ENTITY: Cart
#
# A Cart owns its items and all pricing logic for those items.
# It knows whether it is empty, what it costs, and how to become an Order.
# Collaborators injected via constructor: none -- Cart is a pure domain object.
# ============================================================================

class Cart:
    """A shopping cart that owns its items and knows its own totals."""

    def __init__(self, owner: User) -> None:
        self._owner = owner
        self._items: list[LineItem] = []

    # ------------------------------------------------------------------
    # Properties -- what this Cart IS
    # ------------------------------------------------------------------

    @property
    def owner(self) -> User:
        return self._owner

    @property
    def items(self) -> tuple[LineItem, ...]:
        return tuple(self._items)

    @property
    def is_empty(self) -> bool:
        return len(self._items) == 0

    @property
    def subtotal(self) -> float:
        return round(sum(item.extended_price for item in self._items), 2)

    # ------------------------------------------------------------------
    # Domain responsibilities -- what this Cart CAN DO
    # ------------------------------------------------------------------

    def add(self, product: Product, qty: int) -> None:
        """Add a quantity of a product to the cart. Raises InvalidQuantityError if qty < 1."""
        self._items.append(LineItem(product=product, qty=qty))

    def remove(self, sku: str) -> None:
        """Remove all line items whose product matches sku."""
        self._items = [i for i in self._items if i.product.sku != sku]

    def place_order(self) -> Order:
        """Convert this cart into a confirmed Order, or raise EmptyCartError."""
        if self.is_empty:
            raise EmptyCartError("Cannot place an order from an empty cart.")
        return Order(owner=self._owner, items=self.items)


# ============================================================================
# DOMAIN ENTITY: Order
#
# An Order owns its pricing, tax, and confirmation lifecycle.
# It knows its own total; no service calculates this on its behalf.
# Collaborators injected via constructor: none -- Order is a pure domain object.
# ============================================================================

class Order:
    """A placed order that owns its pricing and confirmation state."""

    def __init__(self, owner: User, items: tuple[LineItem, ...]) -> None:
        self._owner = owner
        self._items = items
        self._confirmed = False

    # ------------------------------------------------------------------
    # Properties -- what this Order IS
    # ------------------------------------------------------------------

    @property
    def owner(self) -> User:
        return self._owner

    @property
    def items(self) -> tuple[LineItem, ...]:
        return self._items

    @property
    def subtotal(self) -> float:
        return round(sum(item.extended_price for item in self._items), 2)

    @property
    def tax(self) -> float:
        return round(self.subtotal * TAX_RATE, 2)

    @property
    def total(self) -> float:
        discounted = self._apply_loyalty_discount(self.subtotal + self.tax)
        return round(discounted, 2)

    @property
    def is_confirmed(self) -> bool:
        return self._confirmed

    # ------------------------------------------------------------------
    # Domain responsibilities -- what this Order CAN DO
    # ------------------------------------------------------------------

    def confirm(self) -> None:
        """Mark this order as confirmed."""
        if self._confirmed:
            raise OrderAlreadyConfirmedError("Order is already confirmed.")
        self._confirmed = True

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_loyalty_discount(self, amount: float) -> float:
        if self._owner.lifetime_spend < LOYALTY_THRESHOLD:
            return amount
        discount_rate = min(self._owner.loyalty_rate, MAX_LOYALTY_DISCOUNT)
        return amount * (1 - discount_rate)


# ============================================================================
# DOMAIN ENTITY: User  (stub -- replace with your real User)
# ============================================================================

@dataclass
class User:
    id: str
    email: str
    lifetime_spend: float = 0.0
    loyalty_rate: float = 0.0
