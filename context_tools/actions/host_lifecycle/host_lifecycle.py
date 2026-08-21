# @toolset-manifest python -m tools manifest host_lifecycle.host_lifecycle:HostLifecycle
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# Do not author behavior from this Python source.
"""Run core host lifecycle actions once per passed context tool."""
from __future__ import annotations

from primitives.actions.action import action, agentic_toolset


@agentic_toolset
class HostLifecycle:
    """Invoke generate / validate / document / satisfy on each context tool argument."""

    @action
    def generate(self, tools: list) -> str:
        """Produce the formal artifact on each passed context tool."""
        for host in self.context_tools(tools):
            host.generate()
        return "When done, run validate."

    @action
    def validate(self, tools: list) -> str:
        """Scan and report pass/fail on each passed context tool."""
        for host in self.context_tools(tools):
            host.validate()
        return "Validation report for artifacts under {session.path}/."

    @action
    def document(self, tools: list, paths: list[str]) -> str:
        """Describe existing code/tests/docs on each passed context tool."""
        for host in self.context_tools(tools):
            host.document(paths)
        return "Document existing state under {session.path}/ - violations flagged, none corrected."

    @action
    def satisfy(self, tools: list) -> str:
        """Validate, fix, validate again on each passed context tool."""
        for host in self.context_tools(tools):
            host.satisfy()
        return "When done, run validate on artifacts under {session.path}/."
