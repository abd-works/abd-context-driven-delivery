"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


VIEW_CURRENT_ORDER_STATUS_MAIN_FLOW: Final = {
    "story":        "View Current Order Status",
    "actor":        "Customer",
    "domain_terms": ("Order", "Order Status", "Timeline Event"),
    "evidence":     ("Order tracking discovery session 2026-05-11",),

    "main_flow": {
        "name":         "customer sees the latest status of a placed order",
        "given": (
            "an Order \"ORD-4200077\" in status placed",
            "And a Timeline Event \"payment authorised\" recorded 10 minutes ago",
        ),
        "interactions": (
            {
                "when": (
                    "the Customer opens the order detail view",
                ),
                "then": (
                    "the Order status placed is displayed prominently",
                    "And the Timeline shows the payment-authorised event",
                ),
            },
        ),
    },
}
