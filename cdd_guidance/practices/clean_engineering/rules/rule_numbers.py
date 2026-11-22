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


def markdown_values() -> dict[str, str]:
    """Each number as the practice's document writes it, by its marker's name: ``{{most.statements}}``, and
    ``{{shipped_limit.code_lines}}`` for the shipped limit of the measure of that name."""
    held = {
        "most.seam_share": f"{round(100 * MOST_SEAM_SHARE)}%",
        "most.statements": str(MOST_STATEMENTS),
        "most.nested_levels": str(MOST_NESTED_LEVELS),
    }
    held.update({f"shipped_limit.{measure}": f"{limit:g}" for measure, limit in code_measures.SHIPPED_LIMITS.items()})
    return held
