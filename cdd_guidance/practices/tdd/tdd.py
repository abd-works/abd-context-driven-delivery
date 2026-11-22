"""TDD: the testing guidance and rules that supplement Clean Engineering code, Stories acceptance tests, BDD development,
and DDD tactics, on in every session."""

from __future__ import annotations

import functools
from pathlib import Path
from typing import TYPE_CHECKING

from harness.agent_tools.agent_tools import agent_toolset
from cdd_guidance.practices.tdd.graph_overlay import TddOverlay
from cdd_guidance.practices.tdd.module_tiers import ModuleTiers
from harness.guidance.practice_supplement import PracticeSupplement

if TYPE_CHECKING:
    from harness.guidance.guidance import FidelityGuidance

# The rule that reads the session's record of test tiers; the fidelities whose section holds it write the tests.
_TIER_RECORD_RULE = "story-tested-at-each-recorded-tier"


@agent_toolset
class Tdd(PracticeSupplement):
    """# Instructions"""

    SHORT_NAME = "TDD"

    def records_for(self, fidelity: FidelityGuidance, files: list[Path] | None = None) -> str:
        """Record, in the session fidelity works in, the test tiers its tests show the module they are for uses, and
        answer what the record holds and what is left for the agent to decide. Only a fidelity whose section holds the
        rule that reads the record (``story-tested-at-each-recorded-tier``) writes the tests it is kept for; any other,
        and a fidelity working in no session, answers nothing."""
        session = fidelity.practice_guidance.session
        keeps_tiers = any(rule.slug == _TIER_RECORD_RULE for rules in self.rules_for(fidelity) for rule in rules)
        if session is None or not keeps_tiers:
            return ""
        return ModuleTiers(fidelity, session).recorded_from(files)

    @functools.cached_property
    def graph_overlay(self) -> TddOverlay:
        """Its facts and graph rules on the practices it supplements, read from its own folder, as a pattern's are."""
        return TddOverlay(self)
