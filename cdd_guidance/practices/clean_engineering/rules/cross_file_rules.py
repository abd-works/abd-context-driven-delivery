"""Rules that read the whole code at once, each of scope all: what one file cannot show, such as a class that builds
what it should own, state handed down through several classes, and a module card the code has moved on from. Each reads the facts the reading records across the graph (``reading/compared_facts.py``)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import SCOPE_ALL, PracticeGraphRule
from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.reading.card_drift import (
    CARD_DRIFT,
    DEPENDENCY_NOT_A_FOLDER,
    DEPENDENCY_NOT_IMPORTED,
    IMPORT_NOT_ON_CARD,
    SEAM_TERM_MISSING,
)
from cdd_guidance.practices.clean_engineering.reading.folder_facts import own_fact
from cdd_guidance.practices.clean_engineering.reading.owned_dependencies import BUILT_ON_EACH_CALL, DEPENDENCIES_TO_OWN
from cdd_guidance.practices.clean_engineering.reading.passed_state import HANDS_DOWN, TAKEN_BY_EVERY_OPERATION
import cdd_guidance.practices.clean_engineering.rules.rule_numbers as rule_numbers

if TYPE_CHECKING:
    from harness.graph.graph import Node
    from harness.graph.rule_context import RuleCheckContext


class PutLogicOnTheOwningResource(PracticeGraphRule):
    """Lists each class that builds another on each call from strings or dicts, or looks it up by name, with the
    relationship it could hold instead (``dependencies_to_own``). Requires a judge: an object built per call may be a
    value or a short-lived request, and only a reading of what both classes are tells it from a part with no owner."""

    slug = "put-logic-on-the-owning-resource"
    node_types = ("OoadClass",)
    requires_judge = True
    scope = SCOPE_ALL

    def check_practice(self, context: "RuleCheckContext") -> list[Finding]:
        return [
            Finding(owner, self._said(owner.name, reached))
            for owner in context.nodes("OoadClass")
            for reached in own_fact(owner, DEPENDENCIES_TO_OWN) or []
        ]

    def _said(self, owner: str, reached: list) -> str:
        """What the candidate says of one dependency the owner reaches: the class, how, and the operations that do it."""
        other, how, through = reached
        where = ", ".join(through)
        if how == BUILT_ON_EACH_CALL:
            return (
                f"Class '{owner}' builds a '{other}' on each call (in {where}), from strings or dicts. Read whether '{owner}' "
                f"should own it: a part it builds once and keeps (composition), or a {other} handed to it and held (association)."
            )
        return (
            f"Class '{owner}' looks up a '{other}' by name (in {where}). Read whether '{owner}' should hold the {other} it "
            "means, handed to it (association), or own it as a part it builds once and keeps (composition)."
        )


class HoldStateOnTheObject(PracticeGraphRule):
    """Lists an operation that starts handing a parameter down, unchanged, to at least the fewest other classes
    (``hands_down``), and a class every operation of which takes one parameter, when it has at least the fewest such
    operations (``taken_by_every_operation``). Requires a judge: a value can rightly pass through, such as the text a
    parser hands to each step, and only a reading tells it from state an object should hold."""

    slug = "hold-state-on-the-object-not-in-parameters"
    node_types = ("Operation", "OoadClass")
    requires_judge = True
    scope = SCOPE_ALL

    def check_practice(self, context: "RuleCheckContext") -> list[Finding]:
        return self._handed_down(context) + self._taken_by_every_operation(context)

    def _handed_down(self, context: "RuleCheckContext") -> list[Finding]:
        return [
            Finding(operation, (
                f"Operation '{chain[0]}' hands its parameter '{parameter}' on unchanged to {classes} other classes: "
                f"{', '.join(chain)}. Read which object should hold the {parameter}, so the operations below it read it there."
            ))
            for operation in context.nodes("Operation")
            for parameter, classes, chain in [own_fact(operation, HANDS_DOWN) or ["", 0, []]]
            if classes >= rule_numbers.FEWEST_CLASSES_HANDED_TO
        ]

    def _taken_by_every_operation(self, context: "RuleCheckContext") -> list[Finding]:
        return [
            Finding(owner, f"Every operation of '{owner.name}' ({count}) takes '{parameter}'. Read whether '{owner.name}' is made for one {parameter} and should hold it.")
            for owner in context.nodes("OoadClass")
            for parameter, count in [own_fact(owner, TAKEN_BY_EVERY_OPERATION) or ["", 0]]
            if count >= rule_numbers.FEWEST_OPERATIONS_TAKING_ONE_PARAMETER
        ]


class SeamNamesCurrentCode(PracticeGraphRule):
    """Reports each thing a module's card says that its code does not (``card_drift``): a seam term that names a class
    or function the module does not declare, a dependency it does not import or that is no folder at all, and a module
    it imports that the card does not name. Each is an exact comparison of names, so the graph decides it."""

    slug = "seam-names-current-code"
    node_types = ("Module",)
    scope = SCOPE_ALL

    _SAID = {
        SEAM_TERM_MISSING: "Module '{module}' card names '{name}' in its seam, which no class in the module declares.",
        DEPENDENCY_NOT_IMPORTED: "Module '{module}' card names the dependency '{name}', which its code does not import.",
        DEPENDENCY_NOT_A_FOLDER: "Module '{module}' card names '{name}', which is no folder of the code.",
        IMPORT_NOT_ON_CARD: "Module '{module}' imports '{name}', which its card does not name among its dependencies.",
    }

    def check_practice(self, context: "RuleCheckContext") -> list[Finding]:
        return [
            Finding(module, self._SAID[kind].format(module=module.name, name=name))
            for module in context.nodes("Module")
            for kind, name in own_fact(module, CARD_DRIFT) or []
        ]


CROSS_FILE_RULES: tuple[PracticeGraphRule, ...] = (
    PutLogicOnTheOwningResource(),
    HoldStateOnTheObject(),
    SeamNamesCurrentCode(),
)
