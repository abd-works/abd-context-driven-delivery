"""The numbers Clean Engineering's rules hold, each named once: the rule's check reads the name here, and the rule's
text in the practice's document takes the same value by a marker (``CleanEngineering.markdown_values``), so the limit
a check reports is the limit its rule states. The measured limits are named in
``measures/code_measures.py`` (``SHIPPED_LIMITS``), beside the tool that takes each measure, and a project's config
may set its own; the most parameters an operation takes is one of them (``parameters_taken``)."""

from __future__ import annotations

from cdd_guidance.practices.clean_engineering.measures import code_measures

# deep-module: the share of a module's methods its seam, the public methods of the classes that leave it, may hold.
MOST_SEAM_SHARE = 0.35
# keep-operations-small-focused: the most statements an operation has.
MOST_STATEMENTS = 20
# simplify-control-flow: the most levels of control flow an operation nests.
MOST_NESTED_LEVELS = 3
# eliminate-duplication: the fewest statements of operations whose bodies match once their names are set aside, for
# them to be listed; shorter bodies, such as getters, read alike without being one behaviour.
FEWEST_SHARED_STATEMENTS = 4
# hold-state-on-the-object-not-in-parameters: the fewest other classes a parameter is handed on to unchanged, and the
# fewest operations of a class that all take one parameter, for either to be listed.
FEWEST_CLASSES_HANDED_TO = 2
FEWEST_OPERATIONS_TAKING_ONE_PARAMETER = 3
# do-not-invent-parallel-object-models: the fewest classes two collections in different files both name, and the share
# of the smaller collection they make up, for one to be listed as a second registry.
FEWEST_CLASSES_REGISTERED_TWICE = 3
LEAST_SHARE_REGISTERED_TWICE = 0.75


def markdown_values() -> dict[str, str]:
    """Each number as the practice's document writes it, by its marker's name: ``{{most.statements}}``, and
    ``{{shipped_limit.code_lines}}`` for the shipped limit of the measure of that name."""
    held = {
        "most.seam_share": f"{round(100 * MOST_SEAM_SHARE)}%",
        "most.statements": str(MOST_STATEMENTS),
        "most.nested_levels": str(MOST_NESTED_LEVELS),
        "fewest.shared_statements": str(FEWEST_SHARED_STATEMENTS),
        "fewest.classes_handed_to": str(FEWEST_CLASSES_HANDED_TO),
        "fewest.operations_taking_one_parameter": str(FEWEST_OPERATIONS_TAKING_ONE_PARAMETER),
        "fewest.classes_registered_twice": str(FEWEST_CLASSES_REGISTERED_TWICE),
        "least.share_registered_twice": f"{round(100 * LEAST_SHARE_REGISTERED_TWICE)}%",
    }
    held.update({f"shipped_limit.{measure}": f"{limit:g}" for measure, limit in code_measures.SHIPPED_LIMITS.items()})
    return held
