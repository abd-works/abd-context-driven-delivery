"""Reverse-engineered rule slugs → model fields graph population must supply.

Used to keep parsers/graph loaders aligned with ``PracticeGraphRule`` checks.
"""

from __future__ import annotations

# Fields are logical keys; graph may store them on ``Node.data`` or via edges.
STORIES_RULE_FIELDS: dict[str, tuple[str, ...]] = {
    "four-to-nine-children": ("child_count:decomposedInto|scenarios|steps",),
    "verb-noun-format": ("node.name",),
    "scenarios-shape": ("steps", "step.phase", "Given|When|Then"),
    "and-chaining": ("step.keyword", "step.continuation", "edges:ands", "when_then_runs"),
    "but-marks-missing-state": ("step.keyword", "step.text"),
    "when-holds-the-operation": ("step.phase", "when_then_runs"),
    "outline-requires-many-permutations": ("scenario.is_outline", "example_count"),
    "examples-trace-domain-model": ("step.concepts", "examples"),
    "flagged-writes-intended-gwt": ("scenario.evidence",),
    "gwt-steps-trace-to-domain-operations": ("step.text", "step.concepts", "step.callees"),
    "plain-english-gwt-steps": ("step.text",),
    "vocabulary-traces-to-domain-source": ("node.name",),
    "kebab-case-paths": ("source.file",),
}

CE_RULE_FIELDS: dict[str, tuple[str, ...]] = {
    "named-seam-and-constraint": ("module_context.md",),
    "missing-module-context": ("module_context.md",),
    "modules-not-model-blocks": ("module_context.md", "language_modules_section"),
    "use-explicit-dependencies": ("operation.constructed_types",),
    "limit-operation-parameters": ("operation.parameters",),
    "deep-module": ("module.public_class_ratio",),
    "one-way-deps": ("module.dependsOn",),
    "no-module-per-class": ("module.class_count",),
    "domain-nouns-only": ("module.name",),
    "write-interactions": ("operation.invokes", "relationship.target"),
}

BDD_RULE_FIELDS: dict[str, tuple[str, ...]] = {
    "observable-behavior": ("observation.source_span",),
    "layer-isolation": ("observation.source_span", "mock_targets"),
    "describe-is-plain-english": ("description.name",),
    "nest-by-enabling-events": ("context.tree", "observation.name"),
}

UX_RULE_FIELDS: dict[str, tuple[str, ...]] = {
    "screen-story-budget": ("screen.story_count",),
    "screen-names-use-domain-terms": ("screen.name", "domain_vocabulary"),
}

BY_PRACTICE = {
    "stories": STORIES_RULE_FIELDS,
    "clean_engineering": CE_RULE_FIELDS,
    "bdd": BDD_RULE_FIELDS,
    "ux": UX_RULE_FIELDS,
}
