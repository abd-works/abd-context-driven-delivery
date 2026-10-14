"""Story rules driven by TypeScript story-map / shared story source."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_DOMAIN_CLASS = re.compile(r"\bclass\s+([A-Z]\w*)\b")
_SCENARIO = re.compile(r"\bscenario\s*\(")
_WRAPPER_CALL = re.compile(r"\b(?:activate|handle|process|run)[A-Z]\w*\s*\(")


class GwtStepsTraceToDomainOperations(PracticeGraphRule):
    slug = "gwt-steps-trace-to-domain-operations"
    node_types = ("Step", "Given", "When", "Then")

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        name = (node.name or "").strip()
        classes = _DOMAIN_CLASS.findall(text)
        if name.isidentifier() or (name.replace("_", "").isalnum() and " " not in name):
            return [f"Step {name!r} does not trace to a domain operation; use the domain type in the step phrase."]
        if not classes:
            return []
        if any(cls.lower() in name.lower() for cls in classes):
            return []
        return [
            f"Step {name!r} does not name a domain concept ({', '.join(classes)}); tie GWT to domain operations."
        ]


class DomainOperationInTheStep(PracticeGraphRule):
    slug = "domain-operation-in-the-step"
    node_types = ("Story", "Step", "Given", "When", "Then")

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        if re.search(r"export function (?:activate|handle|process)\w*\s*\(", text):
            return ["Story shared file exports orchestration instead of calling domain methods in GWT steps."]
        return []


class DomainFixtureExampleFiles(PracticeGraphRule):
    slug = "domain-fixture-example-files"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        path = (node.source.file or "").lower()
        name = path.rsplit("/", 1)[-1]
        if not name.endswith(".examples.ts"):
            return [f"Example file {name!r} should end with .examples.ts under an examples/ folder."]
        if "examples" not in path:
            return [f"Example file {name!r} should live under an examples/ folder."]
        return []


class ExampleRoleNames(PracticeGraphRule):
    slug = "example-role-names"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        text = context.text(node)
        for export in re.findall(r"export const (\w+)", text):
            lowered = export.lower()
            if any(role in lowered for role in ("entered", "stored", "expected", "seed", "fixture")):
                return []
        if "export const" in text:
            return [f"Example exports {node.name!r} without a role name (entered/stored/expected/…)."]
        return []


class OriginatingSubEpicExamples(PracticeGraphRule):
    slug = "originating-sub-epic-examples"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        path = node.source.file or ""
        if "/examples/" in path and "sub-epic" in path.lower():
            return []
        if "epic" in path.lower() and "story" not in path.lower() and "examples" in path:
            return [f"Example {path!r} sits on an epic; place fixtures on the owning story/sub-epic."]
        return []
