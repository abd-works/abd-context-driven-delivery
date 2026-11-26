"""Check the test area's scenarios with this worktree's Stories rules: what each realization rule reports, and what
each Given and When with a realization is linked to.

Run from the worktree root: python test-area/check_realizations.py test-area/pml-web
"""

import sys
from pathlib import Path

from harness.graph.rule_fixture import RuleFixture

from cdd_guidance.practices.ddd.ddd import Ddd
from cdd_guidance.practices.stories.rules import BY_SLUG
from cdd_guidance.practices.stories.stories import Stories

_RULES = ("repositories-called-only-by-the-flow", "code-steps-invoke-code")

root = Path(sys.argv[1])
files = {path.relative_to(root).as_posix(): path.read_text(encoding="utf-8") for path in root.rglob("*.md")}
fixture = RuleFixture(Stories, files, beside=(Ddd,))
for slug in _RULES:
    hits = fixture.hits(BY_SLUG[slug])
    print(f"\n## {slug}: {len(hits)}")
    for hit in hits:
        print(f"- {hit}")

graph = fixture.practice.reading.graph
stories = graph.practices.named("stories").reading.in_graph
print("\n## links")
linked = unlinked = 0
for step in stories.nodes():
    if step.type not in ("Given", "When") or not step.get_fact("realization_calls"):
        continue
    invoked = [edge.child.name for edge in graph.edges.from_parent("invokes", step)]
    linked, unlinked = (linked + 1, unlinked) if invoked else (linked, unlinked + 1)
    print(f"- {step.type} {step.name[:70]!r}: {', '.join(invoked) or 'nothing'}")
print(f"\n{linked} steps with a realization linked, {unlinked} linked to nothing")
