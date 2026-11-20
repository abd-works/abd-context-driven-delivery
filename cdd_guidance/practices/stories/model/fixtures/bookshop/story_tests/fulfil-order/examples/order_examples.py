"""Order examples the Fulfil Order stories share. Seed state: orders the Bookshop already keeps."""

from __future__ import annotations

from src.bookshop.order import Order

PAID_ORDER = Order(number="1001", total=5, payment_status="authorized")
UNPAID_ORDER = Order(number="1002", total=900, payment_status="unpaid")


def paid_order() -> Order:
    return Order(number=PAID_ORDER.number, total=PAID_ORDER.total, payment_status=PAID_ORDER.payment_status)


def unpaid_order() -> Order:
    return Order(number=UNPAID_ORDER.number, total=UNPAID_ORDER.total, payment_status=UNPAID_ORDER.payment_status)
