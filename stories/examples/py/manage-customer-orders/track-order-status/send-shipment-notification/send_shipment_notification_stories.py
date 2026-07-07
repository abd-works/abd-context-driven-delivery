"""Story data — regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


SEND_SHIPMENT_NOTIFICATION: Final = {
    "story":        "Send Shipment Notification",
    "actor":        "System",
    "domain_terms": ("Shipment", "Shipment Notification", "Tracking Number", "Notification Channel"),
    "evidence":     (),
}
