"""The graph-checked supplement's graph rules, shared across the practices it supplements. The framework imports no
practice, so the rule names the practices the spec registered with the catalogue."""
from harness.graph.practice_rule import SharedPracticeGraphRule
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE


class SampleOneOutcome(SharedPracticeGraphRule):
    """A sample rule the supplement checks on BDD observations and Clean Engineering operations."""

    slug = "sample-one-outcome"
    node_types_by_practice = {
        PRACTICE_CATALOGUE.practice_class("bdd"): ("Observation",),
        PRACTICE_CATALOGUE.practice_class("clean_engineering"): ("Operation",),
    }


RULES = (SampleOneOutcome(),)
