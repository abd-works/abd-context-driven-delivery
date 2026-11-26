"""Every practice's graph rules agree with its schema. A rule runs on a node only when the practice's schema lists the
rule on that node's type, so a rule its check judges on a type the schema does not list is never run there in validate,
and its hits are lost."""

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from expects import contain, equal, expect
from mamba import before, description, it

import cdd_guidance.practices  # noqa: F401  (registers the practices)
from harness.graph.schema_rules import PracticeSchema
from harness.graph.practice_reading import rules_in
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE
from cdd_guidance.practices.tdd.tdd import Tdd


def _unlisted(practice) -> list[str]:
    """Each of the practice's own rules, with each node type its check judges that the practice's schema does not list
    the rule on."""
    listed = PracticeSchema(practice).applicable
    package = type(practice).__module__.rsplit(".", 1)[0]
    own = rules_in(f"{package}.rules")
    return sorted(
        f"{practice.key}: {slug} on {node_type}"
        for slug, rule in own.items()
        for node_type in rule.node_types
        if node_type not in listed.get(slug, [])
    )


with description("the graph rules of every practice CDD ships") as self:
    # Reading every practice, its schema, and its rules modules is the slow part, so it is read once for the examples.
    with before.all:
        self.practices = PRACTICE_CATALOGUE.create_all()
        self.unlisted = [gap for practice in self.practices for gap in _unlisted(practice)]

    with it("should check the five practices"):
        expect(len(self.practices)).to(equal(5))

    with it("should list each rule on every node type its check judges, so validate runs it there"):
        expect(self.unlisted).to(equal([]))


with description("the fidelities of every practice CDD ships") as self:
    with before.all:
        self.practices = PRACTICE_CATALOGUE.create_all()

    # A fidelity with no Overview and no Guidance of its own, such as Stories' and BDD's hardening, is held empty until
    # the person writes it, so it has no Scaffold yet.
    with it("should each give a Scaffold once written, which a partition at that fidelity indexes by"):
        missing = sorted(
            f"{practice.key}: {fidelity.name}"
            for practice in self.practices
            for fidelity in practice.fidelities
            if (fidelity.overview or fidelity.guidance) and not fidelity.scaffold
        )
        expect(missing).to(equal([]))


_SAYS_HOW_DECIDED = ("stories", "bdd", "ddd", "ux", "clean_engineering")


def _marker_of(slug: str) -> str:
    return "{{decided." + slug.replace("-", "_") + "}}"


def _rule_lines(practice) -> dict[str, str]:
    """Each rule of the practice's document as it is typed there, by slug: the bullet that opens with the slug."""
    typed = {}
    for line in practice.domain_markdown_path.read_text(encoding="utf-8").splitlines():
        opening = line.lstrip("-* ").lstrip("*`")
        slug = opening.split("`", 1)[0]
        if line.lstrip().startswith(("-", "*")) and slug and slug not in typed:
            typed[slug] = line
    return typed


def _own_checks(practice) -> dict:
    package = type(practice).__module__.rsplit(".", 1)[0]
    return rules_in(f"{package}.rules")


# A rule a program decides is checked; a rule that needs a reading is judged, and its check only lists candidates
# (`requires_judge` on its PracticeGraphRule). The rule's text says which, from that property, so it is typed once.
with description("how each graph rule of a practice is decided, as its rule text says it") as self:
    with before.all:
        # TDD is a supplement, so the catalogue's five practices do not hold it; its rules are marked the same way.
        self.practices = [practice for practice in PRACTICE_CATALOGUE.create_all() if practice.key in _SAYS_HOW_DECIDED] + [Tdd()]
        self.bodies = {rule.slug: rule.body for practice in self.practices for rule in practice.every_rule}
        self.checks = {slug: check for practice in self.practices for slug, check in _own_checks(practice).items()}

    with it("should be marked in the document on every rule a graph rule checks, not typed there"):
        unmarked = sorted(
            f"{practice.key}: {slug}"
            for practice in self.practices
            for slug in _own_checks(practice)
            if slug in _rule_lines(practice) and _marker_of(slug) not in _rule_lines(practice)[slug]
        )
        expect(unmarked).to(equal([]))

    with it("should say a rule a program decides is checked"):
        expect(self.bodies["story-scenarios-at-most-seven"]).to(contain("Checked: the graph decides this rule"))

    with it("should say a rule that requires a judge is judged"):
        expect(self.bodies["when-names-intent-not-interface-gesture"]).to(contain("Judged: the graph only lists candidates"))

    with it("should say judged for exactly the rules that require a judge"):
        said = sorted(slug for slug, body in self.bodies.items() if slug in self.checks and "Judged: the graph only lists candidates" in body)
        expect(said).to(equal(sorted(slug for slug, check in self.checks.items() if check.requires_judge and slug in self.bodies)))

    with it("should leave no marker unfilled in any rule's text"):
        expect(sorted(slug for slug, body in self.bodies.items() if "{{decided." in body)).to(equal([]))
