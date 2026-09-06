# Clean Code — Examples

## Python example

```python
"""
cart.py

Domain area   : cart
Responsibilities: hold items, compute totals, place an order
"""
from __future__ import annotations
from dataclasses import dataclass

TAX_RATE = 0.13
LOYALTY_THRESHOLD = 1000


class EmptyCartError(Exception):
    """Raised when place_order() is called on an empty cart."""


class InvalidQuantityError(Exception):
    """Raised when a line item is added with qty < 1."""


@dataclass(frozen=True)
class Product:
    sku: str
    name: str
    price: float


class LineItem:
    """A chosen quantity of a Product. Gets its price from the Product."""

    def __init__(self, product: Product, qty: int) -> None:
        if qty < 1:
            raise InvalidQuantityError(f"qty for '{product.sku}' must be >= 1")
        self._product = product
        self._qty = qty

    @property
    def extended_price(self) -> float:
        return round(self._product.price * self._qty, 2)


class Cart:
    """A shopping cart that owns its items and knows its own totals."""

    def __init__(self, owner) -> None:
        self._owner = owner
        self._items: list[LineItem] = []

    @property
    def is_empty(self) -> bool:
        return len(self._items) == 0

    @property
    def subtotal(self) -> float:
        return round(sum(i.extended_price for i in self._items), 2)

    def add(self, product: Product, qty: int) -> None:
        self._items.append(LineItem(product=product, qty=qty))

    def place_order(self) -> Order:
        if self.is_empty:
            raise EmptyCartError("Cannot place an order from an empty cart.")
        return Order(owner=self._owner, items=tuple(self._items))


class Order:
    """A placed order that owns its pricing and confirmation lifecycle."""

    def __init__(self, owner, items: tuple[LineItem, ...]) -> None:
        self._owner = owner
        self._items = items
        self._confirmed = False

    @property
    def subtotal(self) -> float:
        return round(sum(i.extended_price for i in self._items), 2)

    @property
    def tax(self) -> float:
        return round(self.subtotal * TAX_RATE, 2)

    @property
    def total(self) -> float:
        return round(self.subtotal + self.tax, 2)

    @property
    def is_confirmed(self) -> bool:
        return self._confirmed

    def confirm(self) -> None:
        if self._confirmed:
            raise RuntimeError("Order is already confirmed.")
        self._confirmed = True
```
