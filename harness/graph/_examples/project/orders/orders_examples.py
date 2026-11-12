"""The named examples the Place Order scenarios use."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class OrderSeed:
    shopper: str
    pets: int


ALICES_ORDER = OrderSeed("alice", 2)
EMPTY_ORDER = OrderSeed("bob", 0)
