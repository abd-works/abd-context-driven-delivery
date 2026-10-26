"""write-interactions — reuse sketch interaction notation in markdown artifacts."""

from __future__ import annotations

from harness.graph.practice_rule import PracticeGraphRule

_MAX_HITS = 2


class WriteInteractions(PracticeGraphRule):
    slug = "write-interactions"
    node_types = ("Operation", "Property", "Invariant", "OoadClass")

    def check(self, node, context) -> list[str]:
        hits = [
            (line, f"Line {line}: use `-> collaborator.operation` sketch notation, not bold **Interaction:** bullets.")
            for line in node.get_fact("bold_interaction_lines", [])
        ] + [
            (line, f"Line {line}: use `//` under the operation for invariants, not bold **Invariant:** bullets.")
            for line in node.get_fact("bold_invariant_lines", [])
        ]
        return [message for _line, message in sorted(hits, key=lambda hit: hit[0])][:_MAX_HITS]
