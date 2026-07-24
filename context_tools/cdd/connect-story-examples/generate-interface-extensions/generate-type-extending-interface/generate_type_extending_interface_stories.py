"""Story data — regeneratable. Do not add logic or imports.

One story, three scenarios (Fake / Isolated / Production).
Owned by clean_engineering generator instructions/templates.
"""

from __future__ import annotations

from typing import Final


GENERATE_TYPE_EXTENDING_INTERFACE: Final = {
    "story": "Generate Type Extending Interface",
    "actor": "Generator",
    "domain_terms": (
        "IType",
        "FakeType",
        "IsolatedType",
        "ProductionType",
        "ExampleFactory",
        "example_key",
    ),
    "evidence": (
        "cdd-sketch.md — Fake/Isolated/Production for any {Type}",
        "context_tools/clean_engineering — example factory pattern",
    ),

    "fake_extension_for_explore_spec": {
        "name": "fake extension for explore/spec",
        "given": (
            "an IType",
            "And examples[example_key] with field values for the types involved",
        ),
        "interactions": (
            {
                "when": (
                    "CE generates FakeType extending IType",
                ),
                "then": (
                    "FakeType implements the public API from examples[example_key]",
                    "And dependencies are not real collaborators",
                ),
            },
        ),
    },

    "isolated_extension_for_a_story_test_tier": {
        "name": "isolated extension for a story-test tier",
        "given": (
            "an IType",
            "And a tier test that must not pull the full stack",
        ),
        "interactions": (
            {
                "when": (
                    "CE generates IsolatedType extending IType",
                ),
                "then": (
                    "IsolatedType implements the real public API for that tier",
                    "And its dependencies are stubs or mocks",
                ),
            },
        ),
    },

    "production_extension_for_a_story_test_tier": {
        "name": "production extension for a story-test tier",
        "given": (
            "an IType",
        ),
        "interactions": (
            {
                "when": (
                    "CE generates ProductionType extending IType",
                ),
                "then": (
                    "ProductionType is the real implementation for that tier",
                    "And tier tests can run against it with real collaborators",
                ),
            },
        ),
    },
}
