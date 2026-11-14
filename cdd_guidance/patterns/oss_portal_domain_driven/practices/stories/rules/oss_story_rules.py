"""OSS Portal story-file rules: the service tier and the citizen journey run the real thing. The shared-story rules the
OSS pattern keeps from LERN (`no-expect-in-given`, `outline-entries-loop-over-examples`) are LERN's own rule classes."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class ServiceTierRunsARealDatabase(PracticeGraphRule):
    """The service spec runs `{Domain}RepositorySql` on a throwaway database with nothing stubbed, so the schema is
    tested with the code."""

    slug = "service-tier-runs-a-real-database"
    node_types = ("ServiceSpec",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{found}` stubs the service tier; run it on a throwaway database with the migrations applied."
            for line, found in node.get_fact("stubs", [])
        ]


class JourneyTestPerRelease(PracticeGraphRule):
    """The journey test runs the portal, BFF, Apigee, and service with nothing stubbed or intercepted, because the pack
    verifies every release with a representative citizen journey (OP-05, APP-09)."""

    slug = "journey-test-per-release"
    node_types = ("JourneySpec",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{found}` stubs part of the citizen journey; run every layer for real."
            for line, found in [*node.get_fact("stubs", []), *node.get_fact("stubbed_requests", [])]
        ]
