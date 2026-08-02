"""Shopping cart — line items and subtotal."""

from __future__ import annotations

from decimal import Decimal


class LineItem:
    def __init__(self, product: str, quantity: int, unit_price: Decimal) -> None:
        self._product = product
        self._quantity = quantity
        self._unit_price = unit_price

    @property
    def product(self) -> str:
        return self._product

    @property
    def quantity(self) -> int:
        return self._quantity

    @property
    def unit_price(self) -> Decimal:
        return self._unit_price

    @property
    def extended_price(self) -> Decimal:
        return self._unit_price * self._quantity


class Cart:
    def __init__(self) -> None:
        self._line_items: list[LineItem] = []

    @property
    def line_items(self) -> list[LineItem]:
        return list(self._line_items)

    def add_item(self, product: str, quantity: int, unit_price: Decimal) -> None:
        self._line_items.append(LineItem(product, quantity, unit_price))

    def subtotal(self) -> Decimal:
        return sum(item.extended_price for item in self._line_items)
