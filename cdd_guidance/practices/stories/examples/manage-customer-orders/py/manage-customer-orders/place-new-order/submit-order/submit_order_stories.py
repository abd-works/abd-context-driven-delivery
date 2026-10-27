"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


SUBMIT_ORDER_MAIN_FLOW: Final = {
    "story":        "Submit Order",
    "actor":        "Customer",
    "domain_terms": ("Order", "Cart", "Payment Method", "Order Confirmation", "Order Number"),
    "evidence":     ("Checkout workshop 2026-05-04 - happy-path wall walk",),

    "main_flow": {
        "name":         "order submitted with valid cart and payment",
        "given": (
            "a Cart with three Items totalling 149.98 USD",
            "And a Payment Method on file \"Visa ending 4242\"",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer confirms and submits the Order",
                ),
                "then": (
                    "an Order Confirmation is issued with an Order Number",
                    "And the Cart is emptied",
                ),
            },
        ),
    },
}

SUBMIT_ORDER: Final = {
    "story":        "Submit Order",
    "actor":        "Customer",
    "domain_terms": ("Order", "Cart", "Payment Method", "Order Number", "Order Status"),
    "evidence":     ("Checkout workshop 2026-05-04 - happy-path wall walk", "API spec v3 - POST /orders #\"submission errors\""),

    "submission_succeeds": {
        "name":         "order accepted for a valid cart and payment method",
        "given": (
            "a Cart \"CART-9001\" containing 3 Items totalling 149.98 USD",
            "And a Payment Method *\"Visa ****4242\" with status authorised*",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits the Order",
                ),
                "then": (
                    "an Order is created with status placed",
                    "And an Order Number matching pattern ORD-\\d{7} is returned",
                ),
            },
        ),
    },

    "submission_rejected_for_declined_card": {
        "name":         "order rejected when payment method is declined",
        "given": (
            "a Cart \"CART-9002\" totalling 89.50 USD",
            "And a Payment Method *\"MasterCard ****5150\" in status declined*",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits the Order",
                ),
                "then": (
                    "the Order is rejected with reason payment_declined",
                    "But the Cart contents are preserved for retry",
                ),
            },
        ),
    },
}

SUBMIT_ORDER_OUTLINE: Final = {
    "story":        "Submit Order - outline",
    "actor":        "Customer",
    "domain_terms": ("Order", "Payment Method", "Order Status"),
    "evidence":     ("API spec v3 - POST /orders #\"submission errors\"",),

    "outline": {
        "name":         "submission result varies with payment method status",
        "given": (
            "a Cart {cart_id} totalling {cart_total} {currency}",
            "And a Payment Method {payment_method} in status {payment_status}",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits the Order",
                ),
                "then": (
                    "the Order status is set to {order_status}",
                ),
            },
        ),
    },
}
