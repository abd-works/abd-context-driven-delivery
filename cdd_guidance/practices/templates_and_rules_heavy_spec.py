"""One spec for every practice: each template, filled in and read where its fidelity declares its files, passes the
practice's own graph rules; and each checked graph rule has a failing example and a repaired one.

Exploratory testing, shortcoming 8: a rule, its template and its check were kept apart with nothing that compared
them, and one rule its own template failed made more than half of a session's graph findings. Heavy: every template
is read by a real load of a folder of its own, and every example pair by two.

What is not yet so is written here by name, so the spec fails when the list grows and when it shrinks: a template the
practice reads no node from is not checked by any rule, and a rule with no example pair is proved by nothing here.
"""
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import equal, expect
from mamba import before, context, description, included_context, it, shared_context

import cdd_guidance.practices  # noqa: F401 - registers the practices with the practice catalogue
from cdd_guidance.practices.template_checks import RuleExamples, TemplateCheck
from harness.guidance.practice_catalogue import PRACTICE_CATALOGUE

# Templates the practice reads no node from, so no graph rule runs on them.
UNREAD = {
    "stories": [],
    "ddd": [],
    "ux": [],
    "bdd": [],
    "clean_engineering": [],
}
# What Clean Engineering's own rules report on its templates today: nothing, since its model template types every parameter.
CLEAN_ENGINEERING_TEMPLATE_FINDINGS: dict[str, list[str]] = {}
# Checked graph rules with no failing and repaired example yet. Each is a rule a change can break with no spec to say so.
WITHOUT_A_PAIR = {
    "stories": [
        "and-chaining",
        "behavioral-and-system-observable-outcomes",
        "branch-on-mechanical-uniqueness",
        "but-marks-missing-state",
        "code-steps-invoke-code",
        "domain-terms-link-to-model",
        "examples-trace-domain-model",
        "flagged-writes-intended-gwt",
        "given-names-complex-state-root-first",
        "scenario-names-continuation",
        "scenarios-shape",
        "when-names-intent-not-interface-gesture",
    ],
    "ddd": [],
    "ux": [],
    "bdd": [],
    "tdd": [],
}
# Example pairs that do not hold today. Both Stories folders hold an examples file and no story test that imports it,
# so the read finds no Example for the rule to judge: the rules were moved onto Example nodes and the folders were not.
PAIRS_THAT_DO_NOT_HOLD = {
    "stories": [
        "domain-fixture-example-files: domain-fixture-example-files: expected violations on the failing fixture, got none",
        "examples-export-data-not-repository: examples-export-data-not-repository: expected violations on the failing fixture, got none",
    ],
    "ddd": [],
    "ux": [],
    "bdd": [],
    "tdd": [],
}


with shared_context("a practice's templates and rules"):
    with before.all:
        self.practice = next(practice for practice in PRACTICE_CATALOGUE.create_all() if practice.key == self.key)
        self.templates = TemplateCheck(self.practice)

    with it("should pass each template through the practice's own graph rules"):
        expect(self.templates.findings()).to(equal(self.template_findings))

    with it("should read a node from every template but those named as holding none"):
        expect(self.templates.unread()).to(equal(UNREAD[self.key]))

    with it("should leave no marker for a value its code holds unfilled in its document or a template"):
        expect(self.templates.unfilled_markers()).to(equal([]))


with shared_context("a practice's checked rules"):
    with before.all:
        self.examples = RuleExamples(self.key)

    with it("should have a failing and a repaired example for every checked graph rule but those named"):
        expect(self.examples.without_a_pair()).to(equal(WITHOUT_A_PAIR[self.key]))

    with it("should flag each failing example and pass each repaired one, but for the pairs named"):
        expect(self.examples.failing_pairs()).to(equal(PAIRS_THAT_DO_NOT_HOLD[self.key]))


with description("every practice's templates and rules") as self:
    with context("for Stories"):
        with before.all:
            self.key, self.template_findings = "stories", {}

        with included_context("a practice's templates and rules"):
            pass

        with included_context("a practice's checked rules"):
            pass

    with context("for DDD"):
        with before.all:
            self.key, self.template_findings = "ddd", {}

        with included_context("a practice's templates and rules"):
            pass

        with included_context("a practice's checked rules"):
            pass

    with context("for UX"):
        with before.all:
            self.key, self.template_findings = "ux", {}

        with included_context("a practice's templates and rules"):
            pass

        with included_context("a practice's checked rules"):
            pass

    with context("for BDD"):
        with before.all:
            self.key, self.template_findings = "bdd", {}

        with included_context("a practice's templates and rules"):
            pass

        with included_context("a practice's checked rules"):
            pass

    # TDD is a supplement with no template of its own; its graph rules have their pairs like any practice's.
    with context("for the TDD supplement"):
        with before.all:
            self.key = "tdd"

        with included_context("a practice's checked rules"):
            pass

    with context("for Clean Engineering, whose findings its owner settles"):
        with before.all:
            self.key, self.template_findings = "clean_engineering", CLEAN_ENGINEERING_TEMPLATE_FINDINGS

        with included_context("a practice's templates and rules"):
            pass
