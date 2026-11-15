"""The sample supplement's graph rules shared across the practices it supplements."""
from cdd_guidance.practices.bdd.bdd import Bdd
from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering
from harness.graph.practice_rule import SharedPracticeGraphRule


class SampleOneOutcome(SharedPracticeGraphRule):
    """A sample rule the supplement checks on BDD observations and Clean Engineering operations."""

    slug = "sample-one-outcome"
    node_types_by_practice = {Bdd: ("Observation",), CleanEngineering: ("Operation",)}


RULES = (SampleOneOutcome(),)
