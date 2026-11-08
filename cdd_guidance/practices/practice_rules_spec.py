"""Every practice's graph rules agree with its schema. A rule runs on a node only when the practice's schema lists the
rule on that node's type, so a rule its check judges on a type the schema does not list is never run there in validate,
and its hits are lost."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import equal, expect
from mamba import description, it

import cdd_guidance.practices  # noqa: F401  (registers the practices)
from harness.graph.schema_rules import PracticeSchema
from harness.guidance.guidance import rules_in
from harness.guidance.practice_catalogue import PracticeCatalogue


def _unlisted(practice) -> list[str]:
    """Each of the practice's own rules, with each node type its check judges that the practice's schema does not list
    the rule on."""
    listed = PracticeSchema(practice).applicable
    own = rules_in(f"{practice.package}.rules")
    return sorted(
        f"{practice.key}: {slug} on {node_type}"
        for slug, rule in own.items()
        for node_type in rule.node_types
        if node_type not in listed.get(slug, [])
    )


with description("the graph rules of every practice CDD ships"):
    with it("should check the five practices"):
        expect(len(PracticeCatalogue.practices())).to(equal(5))

    with it("should list each rule on every node type its check judges, so validate runs it there"):
        expect([gap for practice in PracticeCatalogue.practices() for gap in _unlisted(practice)]).to(equal([]))
