"""The rules about unused and disconnected code: a class or an operation nothing uses, one only a call the read could
not join may use, a public operation only its own folder calls, a class joined to others only by inheritance, and a
package of one class. Each asks how files use one another, so each runs over the whole working copy (scope ``all``)
and reads *CodeUse* once for the practice it checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from harness.graph.practice_rule import SCOPE_ALL
from harness.graph.violation import Finding

from cdd_guidance.practices.clean_engineering.rules.code_use import CodeUse
from cdd_guidance.practices.clean_engineering.rules.production_code_rule import ProductionCodeRule

if TYPE_CHECKING:
    from harness.graph.rule_context import RuleCheckContext

# What each kind of node a rule reports is called in its message.
_KIND = {"OoadClass": "Class", "Operation": "Operation", "Property": "Property"}
# Where a project names the ways it reaches code besides calls and imports, which every message points the reader to.
_WAYS = "the `code_reach` ways its `.context/config.json` names"


class DeleteUnusedClasses(ProductionCodeRule):
    """A production class no other class uses, which uses no other class, which no member of another class or module
    function calls into, and which no way the project reaches code reaches: no use, delete it with its specs."""

    slug = "delete-unused-classes"
    node_types = ("OoadClass",)
    scope = SCOPE_ALL
    code_fidelity_only = True

    def check_practice(self, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"Class '{node.name}': no use — delete it with its specs. No class uses it or is used by it, nothing calls into it, and none of {_WAYS} reaches it.")
            for node in CodeUse(context).unused_classes()
        ]


class DeleteUnusedOperations(ProductionCodeRule):
    """A public production operation of a used class that nothing calls, through its class or its family, and that no
    way the project reaches code reaches: no use, delete it with its specs. A call the read joined by a guess counts as
    a use."""

    slug = "delete-unused-operations"
    node_types = ("Operation", "Property")
    scope = SCOPE_ALL
    code_fidelity_only = True

    def check_practice(self, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"{_KIND[node.type]} '{node.name}': no use — delete it with its specs. Nothing calls it, on its class or on a class of its family, and none of {_WAYS} reaches it.")
            for node in CodeUse(context).unused_operations()
        ]


class CheckUseTheGraphCannotSee(ProductionCodeRule):
    """A class or a public operation nothing the graph sees uses, which a call the read could not join may reach: a
    call on a value no type says, near it. The graph cannot tell whether that call reaches it, so it requires a judge:
    whoever reads the calls deletes it when none does."""

    slug = "check-use-the-graph-cannot-see"
    requires_judge = True
    node_types = ("OoadClass", "Operation", "Property")
    scope = SCOPE_ALL
    code_fidelity_only = True

    def check_practice(self, context: RuleCheckContext) -> list[Finding]:
        use = CodeUse(context)
        listed = [*use.classes_unseen_calls_may_use(), *use.operations_unseen_calls_may_reach()]
        return [Finding(node, self._said(node, use)) for node in listed]

    def _said(self, node, use: CodeUse) -> str:
        kind = _KIND[node.type]
        unseen = use.unseen_calls_reaching(node)
        why = (f"{unseen} calls in the files that could reach it are made on values no type says, and one may reach it"
            if unseen else "another file imports its name, but the read joined no call to it")
        return f"{kind} '{node.name}': no use the graph can see, but {why}. Read them, and delete it with its specs if none reaches it."


class MakeModuleOnlyOperationsPrivate(ProductionCodeRule):
    """A public operation of a class on its module's seam that only code inside the module calls, which no way the
    project reaches code reaches, and which overrides nothing: the module's seam is wider than its use. Whether to make it private, or whether another
    module should call it, is a reading, so it requires a judge."""

    slug = "make-module-only-operations-private"
    requires_judge = True
    node_types = ("Operation",)
    scope = SCOPE_ALL
    code_fidelity_only = True

    def check_practice(self, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(node, f"Operation '{node.name}': public on a class its module shows other modules, but only code inside the module calls it. "
                "Make it private to the module, or say which other module should call it.")
            for node in CodeUse(context).operations_called_only_in_their_module()
        ]


class ConnectDisconnectedClasses(ProductionCodeRule):
    """A used class joined to other classes only by inheritance, or by nothing: no class of its family holds, is
    handed, creates, calls or reads another, or is held or reached by one. Either the model misses a relationship, or
    the class is a helper callers hand data to instead of an object its owner holds; which, needs a reading."""

    slug = "connect-disconnected-classes"
    requires_judge = True
    node_types = ("OoadClass",)
    scope = SCOPE_ALL
    code_fidelity_only = True

    def check_practice(self, context: RuleCheckContext) -> list[Finding]:
        return [Finding(node, self._said(node.name, family)) for node, family in CodeUse(context).disconnected_classes()]

    def _said(self, name: str, family: list) -> str:
        joined = f"joined to other classes only by inheritance ({', '.join(sorted(member.name for member in family))})" if family else "joined to no other class"
        return (f"Class '{name}': {joined}. Name the class that owns it, and make it a part (composition) or a held collaborator "
            "(association) of that class, or say why it stands alone.")


class MergeOneClassPackages(ProductionCodeRule):
    """A package, a folder with no module card of its own, that holds one class and no folder. A package groups
    cohesive classes; one class alone is unused (delete), part of a bigger package (merge), or not fully modelled,
    which needs a reading."""

    slug = "merge-one-class-packages"
    requires_judge = True
    node_types = ("Package",)
    scope = SCOPE_ALL
    code_fidelity_only = True

    def check_practice(self, context: RuleCheckContext) -> list[Finding]:
        return [
            Finding(package, f"Package '{package.name}': holds only the class {held.name}. Merge it into the package or module it belongs "
                "with, delete it if nothing uses it, or model the classes it is missing.")
            for package, held in CodeUse(context).one_class_packages()
        ]


CODE_USE_RULES: tuple = (
    DeleteUnusedClasses(),
    DeleteUnusedOperations(),
    CheckUseTheGraphCannotSee(),
    MakeModuleOnlyOperationsPrivate(),
    ConnectDisconnectedClasses(),
    MergeOneClassPackages(),
)
