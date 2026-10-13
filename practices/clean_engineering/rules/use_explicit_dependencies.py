from __future__ import annotations

import re

from harness.graph.practice_rule import PracticeGraphRule

from practices.clean_engineering.rules._span import class_body, constructor_body


class UseExplicitDependencies(PracticeGraphRule):
    slug = "use-explicit-dependencies"
    node_types = ("OoadClass",)

    def check(self, node, context) -> list[str]:
        oclass = context.ce_class(node)
        if oclass is not None:
            for op in oclass.operations:
                if op.name not in {"__init__", "constructor"}:
                    continue
                for type_name, _line in op.constructed_types:
                    if type_name != node.name:
                        return [f"Class '{node.name}' constructs '{type_name}' inside its constructor."]
            return []
        text = context.text(node)
        body = class_body(text, node.name)
        constructor = constructor_body(body)
        if not constructor:
            return []
        for created in re.findall(r"\bnew\s+([A-Z]\w*)", constructor):
            if created != node.name:
                return [f"Class '{node.name}' constructs '{created}' inside its constructor."]
        return []
