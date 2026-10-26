"""acceptance_tests fidelity — example and fixture rules."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

class DomainFixtureExampleFiles(PracticeGraphRule):
    slug = "domain-fixture-example-files"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        path = (node.source.file or "").lower()
        module = (node.get_fact("imported_modules") or {}).get(node.name)
        if module is not None:
            path = module.lower() + ".ts"
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
        exports = node.get_fact("export_names", [])
        for export in exports:
            lowered = export.lower()
            if any(role in lowered for role in ("entered", "stored", "expected", "seed", "fixture")):
                return []
        if exports:
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

class ExamplesExportDataNotRepository(PracticeGraphRule):
    slug = "examples-export-data-not-repository"
    node_types = ("Example",)

    def check(self, node, context) -> list[str]:
        relative = node.source.file or ""
        if "repository" in relative.lower() and "examples" in relative.lower():
            return [f"Example file '{relative}' looks like a repository; export data fixtures instead."]
        return []
