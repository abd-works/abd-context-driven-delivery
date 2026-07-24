"""Story data — regeneratable. Do not add logic or imports."""

from __future__ import annotations

from typing import Final


GENERATE_SCENARIO_STEPS_THAT_CALL_FACTORY_METHODS: Final = {
    "story": "Generate Scenario Steps That Call Factory Methods",
    "actor": "Generator",
    "domain_terms": ("Scenario", "helper", "TypeExampleFactory", "FakeType"),
    "evidence": (
        "cdd-sketch.md — steps -> helper -> factory -> Fake",
        "context_tools/stories — factory-objects-in-scenarios",
    ),

    "main_flow": {
        "name": "explore/spec steps go helper then factory then Fake",
        "given": (
            "examples[example_key] bundling the IType payloads needed",
            "And TypeExampleFactory.example_method",
        ),
        "interactions": (
            {
                "when": (
                    "Stories generates exploration/spec scenario steps",
                ),
                "then": (
                    "steps call helper methods",
                    "And those helpers call TypeExampleFactory.example_method",
                    "And the factory returns FakeType objects used in the scenario",
                ),
            },
        ),
    },
}
