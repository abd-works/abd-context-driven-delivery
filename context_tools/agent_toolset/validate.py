"""Agentic validate against the current context."""
from __future__ import annotations

from typing import Any

from context_tools.agent_toolset.scan import Rule


class Validate:
    def validate(self, tools: Any, rule: Rule | None = None) -> str:
        if rule is not None:
            return rule.validate()
        return tools.rules.validate()
