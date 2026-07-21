"""Story data — regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


GENERATE_SUB_EPIC_THAT_IMPORTS_FACTORIES: Final = {
    "story": "Generate Sub-Epic That Imports Factories",
    "actor": "Generator",
    "domain_terms": ("SubEpic", "TypeExampleFactory", "sub-epic helper"),
    "evidence": (
        "cdd-sketch.md — sub-epic helper imports epic + local factories",
        "contexts/stories — helpers-import-factories",
    ),

    "main_flow": {
        "name": "sub-epic helper imports epic factories plus local factories",
        "given": (
            "an epic helper importing TypeExampleFactory",
        ),
        "interactions": (
            {
                "when": (
                    "Stories generates the sub-epic helper",
                ),
                "then": (
                    "the sub-epic helper imports epic factories and local ones",
                ),
            },
        ),
    },
}
