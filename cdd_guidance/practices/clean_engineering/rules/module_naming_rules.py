"""Module naming and shape rules — folder facts and the classes the graph places in each folder."""

from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

_VERB_MODULE = re.compile(
    r"(^|/)(manage|process|handle|run|execute|build|create|update|delete|get|set)[-_]",
    re.I,
)
_BAD_SUFFIX = re.compile(r"(Model|Runtime|Service|Manager|Helper|Util|Utils|Processor)$")


class DomainNounsOnly(PracticeGraphRule):
    slug = "domain-nouns-only"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
        name = (node.name or "").strip()
        if not name:
            return []
        if _VERB_MODULE.search(name.replace(".", "/")):
            return [f"Module {name!r} reads like an action verb path, not a domain noun."]
        leaf = name.split(".")[-1]
        if _BAD_SUFFIX.search(leaf):
            return [f"Module {name!r} uses technical suffix {leaf!r}; use a domain noun."]
        return []


class NoModulePerClass(PracticeGraphRule):
    slug = "no-module-per-class"
    node_types = ("Module",)

    def check(self, node, context) -> list[str]:
        if node.get_fact("is_a_in_context"):
            return [
                f"Module {node.name!r} module-context uses '*is a type of*'; "
                "generalisation belongs in model, not modules fidelity."
            ]
        if node.get_fact("child_parent_in_context"):
            return [
                f"Module {node.name!r} module-context uses 'Child : Parent'; "
                "use model fidelity for generalisation."
            ]
        if _public_classes_in(node, context) == 1 and node.get_fact("public_source_files", 0) <= 1:
            return [
                f"Module {node.name!r} exposes a single class in one file; "
                "group cohesive classes or merge into an existing module."
            ]
        return []


def _public_classes_in(folder_node, context) -> int:
    count = 0
    for class_node in context.practice.nodes.get("OoadClass", []):
        file_name = (class_node.source.file or "").rsplit("/", 1)[-1]
        if class_node.get_fact("folder") == folder_node.node_id and not file_name.startswith(("_", "test_")):
            count += 1
    return count
