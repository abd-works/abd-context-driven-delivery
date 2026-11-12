"""Orders a shopper places. Known issue: place takes five parameters, over the limit."""

from __future__ import annotations


class Order:
    def __init__(self, shopper: str) -> None:
        self.shopper = shopper
        self.lines: list[str] = []

    def place(self, a: str, b: str, c: str, d: str, e: str) -> None:
        self.lines.extend([a, b, c, d, e])
        self.confirm()

    def confirm(self) -> bool:
        return bool(self.lines)

    @property
    def total(self) -> int:
        return len(self.lines)
