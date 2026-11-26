"""UX graph rule classes."""

from cdd_guidance.practices.ux.rules.canvas_rules import EveryScenarioHasAState, ScenarioListedOnce, ScreenFollowsScenario, ScreenIsAPrototype
from cdd_guidance.practices.ux.rules.canvas_source_rules import PositionsHoldNoData, ScreenFilesFromProduction
from cdd_guidance.practices.ux.rules.screen_rules import ScreenNamesUseDomainTerms, ScreenStoryBudget

RULES: tuple = (
    ScreenStoryBudget(),
    ScreenNamesUseDomainTerms(),
    ScreenIsAPrototype(),
    ScreenFollowsScenario(),
    EveryScenarioHasAState(),
    ScenarioListedOnce(),
    ScreenFilesFromProduction(),
    PositionsHoldNoData(),
)
BY_SLUG = {rule.slug: rule for rule in RULES}

__all__ = ["BY_SLUG", "RULES"]
