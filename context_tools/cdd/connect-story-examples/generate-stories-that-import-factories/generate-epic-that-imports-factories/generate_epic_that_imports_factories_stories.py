"""Story data — regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


GENERATE_EPIC_THAT_IMPORTS_FACTORIES: Final = {
    "story": "Generate Epic That Imports Factories",
    "actor": "Generator",
    "domain_terms": ("Epic", "TypeExampleFactory", "epic helper"),
    "evidence": (
        "cdd-sketch.md — epic helper imports factories",
        "context_tools/stories — helpers-import-factories",
    ),

    "main_flow": {
        "name": "epic helper imports factories and exposes methods that call them",
        "given": (
            "a TypeExampleFactory emitted by clean_engineering",
        ),
        "interactions": (
            {
                "when": (
                    "Stories generates the epic helper",
                ),
                "then": (
                    "the epic helper imports TypeExampleFactory",
                    "And exposes helper methods that call factory methods",
                ),
            },
        ),
    },
}
