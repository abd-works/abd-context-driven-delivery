"""LERN behavior-file rules — read the facts recorded on each LERN behavior file node."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule


class SharedBehaviorStaysTierFree(PracticeGraphRule):
    """A shared behavior runs on every tier, so it reaches the tier only through its driver."""

    slug = "shared-behavior-stays-tier-free"
    node_types = ("BehaviorShared",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` ties the shared behavior to one tier; "
            f"add an operation to the driver and call it from here."
            for line, code in node.get_fact("tier_reaches", [])
        ]


class TierRunsSharedBehavior(PracticeGraphRule):
    """A tier file that states its own copy of a behavior drifts from the shared one."""

    slug = "tier-runs-shared-behavior"
    node_types = ("BehaviorDomain", "BehaviorServer", "BehaviorPlaywright", "BehaviorE2e")

    def check(self, node, context) -> list[str]:
        if node.get_fact("runs_shared_behavior", False):
            return []
        return [f"{node.source.file}: runs no shared behavior; call itBehavesLike with the behavior this tier proves."]


class ServerTierCallsTheRealThing(PracticeGraphRule):
    """The server tier exists to prove the node against what it really talks to."""

    slug = "server-tier-calls-the-real-thing"
    node_types = ("BehaviorServer",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` stubs what the server tier must call for real; "
            f"give the node a throwaway store or project instead."
            for line, code in node.get_fact("stubs", [])
        ]


class E2eRunsTheWholeStack(PracticeGraphRule):
    """A stubbed request in an end-to-end run proves less than the tier below it."""

    slug = "e2e-runs-the-whole-stack"
    node_types = ("BehaviorE2e",)

    def check(self, node, context) -> list[str]:
        return [
            f"{node.source.file}:{line}: `{code}` stubs part of the stack; "
            f"the e2e tier runs the page, the server, and the real store or tool together."
            for line, code in [*node.get_fact("stubs", []), *node.get_fact("stubbed_requests", [])]
        ]
