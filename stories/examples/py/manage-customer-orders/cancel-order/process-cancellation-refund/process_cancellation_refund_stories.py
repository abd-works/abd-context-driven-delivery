"""Story data — regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


PROCESS_CANCELLATION_REFUND: Final = {
    "story":        "Process Cancellation Refund",
    "actor":        "System",
    "domain_terms": ("Cancellation", "Refund", "Refund Amount", "Payment Method"),
    "evidence":     (),
}
