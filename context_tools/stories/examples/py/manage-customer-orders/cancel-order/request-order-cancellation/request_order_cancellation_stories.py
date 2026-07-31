"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


REQUEST_ORDER_CANCELLATION: Final = {
    "story":        "Request Order Cancellation",
    "actor":        "Customer",
    "domain_terms": ("Order", "Cancellation Request", "Cancellation Reason", "Order Status"),
    "evidence":     ("Cancellation policy doc v2 #3", "Customer support call review 2026-05-18"),

    "cancellation_accepted_before_shipment": {
        "name":         "cancellation accepted while the order is still placed",
        "given": (
            "an Order \"ORD-4200080\" in status placed",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits a Cancellation Request with reason \"changed mind\"",
                ),
                "then": (
                    "the Order status changes to cancelled",
                    "And the Cancellation Request records reason \"changed mind\"",
                ),
            },
        ),
    },

    "cancellation_rejected_after_shipment": {
        "name":         "cancellation rejected once the shipment is on the way",
        "given": (
            "an Order \"ORD-4200081\" in status shipped",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer submits a Cancellation Request",
                ),
                "then": (
                    "the Cancellation Request is rejected",
                    "But the Order remains in status shipped",
                ),
            },
        ),
    },
}
