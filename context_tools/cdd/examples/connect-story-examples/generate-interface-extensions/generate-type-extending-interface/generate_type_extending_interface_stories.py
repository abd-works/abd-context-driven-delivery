"""Story data - regeneratable. Do not add logic or imports.

One story, three scenarios (Fake / Isolated / Production modes).
Owned by clean_engineering generator instructions/templates.
"""

from __future__ import annotations

from typing import Final


GENERATE_TYPE_EXTENDING_INTERFACE: Final = {
    "story": "Generate Type Extending Interface",
    "actor": "Generator",
    "domain_terms": (
        "IType",
        "Type",
        "TypeExampleFactory",
        "example_key",
        "mode",
    ),
    "evidence": (
        "cdd-sketch.md - Fake/Isolated/Production modes for any {Type}",
        "context_tools/clean_engineering - example factory pattern",
        "context_tools/cdd/example-factories - modes are not subclasses",
    ),

    "fake_mode_for_explore_spec": {
        "name": "fake mode for explore/spec",
        "given": (
            "an IType seam",
            "And examples[example_key] with field values for the types involved",
        ),
        "interactions": (
            {
                "when": (
                    "CE generates TypeExampleFactory that builds IType in fake mode",
                ),
                "then": (
                    "the factory returns IType filled from examples[example_key]",
                    "And dependencies are not real collaborators",
                ),
            },
        ),
    },

    "isolated_mode_for_a_story_test_tier": {
        "name": "isolated mode for a story-test tier",
        "given": (
            "an IType seam",
            "And a tier test that must not pull the full stack",
        ),
        "interactions": (
            {
                "when": (
                    "CE generates TypeExampleFactory that builds Type in isolated mode",
                ),
                "then": (
                    "the factory returns Type with ctor-injected mocks or stubs",
                    "And no FakeType / IsolatedType / ProductionType subclasses are emitted",
                ),
            },
        ),
    },

    "production_mode_for_a_story_test_tier": {
        "name": "production mode for a story-test tier",
        "given": (
            "an IType seam",
        ),
        "interactions": (
            {
                "when": (
                    "CE generates TypeExampleFactory that builds Type in production mode",
                ),
                "then": (
                    "the factory returns Type with real collaborators",
                    "And tier tests can run against the production implementation",
                ),
            },
        ),
    },
}
