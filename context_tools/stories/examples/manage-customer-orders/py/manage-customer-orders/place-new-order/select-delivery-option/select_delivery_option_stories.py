"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


SELECT_DELIVERY_OPTION: Final = {
    "story":        "Select Delivery Option",
    "actor":        "Customer",
    "domain_terms": ("Delivery Option", "Delivery Speed", "Delivery Fee", "Estimated Arrival"),
    "evidence":     (),
}
