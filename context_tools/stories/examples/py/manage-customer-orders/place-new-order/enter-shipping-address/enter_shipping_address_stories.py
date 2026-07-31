"""Story data - regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


ENTER_SHIPPING_ADDRESS: Final = {
    "story":        "Enter Shipping Address",
    "actor":        "Customer",
    "domain_terms": ("Shipping Address", "Address Line", "Postal Code", "Country"),
    "evidence":     (),
}
