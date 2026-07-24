"""Mamba spec for `a Scenario`.

Mirrors the `## Scenario` block of bdd-context.md 1:1.
"""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "context_tools" / "stories" / "src" / "context_tools" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, be_empty, expect

from context_tools.stories.story_model.scenario import (
    Clause,
    Interaction,
    Phase,
    Scenario,
)
from context_tools.stories.story_model.update_report import TranslationError


def _clause(text: str, phase: Phase) -> Clause:
    is_cont = text.startswith("And ") or text.startswith("But ")
    return Clause(text=text, phase=phase, is_continuation=is_cont)


def _given(text: str) -> Clause:
    return _clause(text, Phase.GIVEN)


def _when(text: str) -> Clause:
    return _clause(text, Phase.WHEN)


def _then(text: str) -> Clause:
    return _clause(text, Phase.THEN)


with description("a Scenario") as self:
    with it("should report itself as a leaf StoryNode"):
        scenario = Scenario("Submit transfer before cutoff", 1)
        expect(scenario.semantic_type()).to(equal("Scenario"))

    with it("should return an empty list from childCollections"):
        scenario = Scenario("Submit transfer before cutoff", 1)
        expect(scenario.child_collections(scenario)).to(equal([]))

    with context(
        "that has been translated from another Scenario of the same semantic type"
    ):
        with before.each:
            source = Scenario("Original name", 1, story_name="My Story")
            source.given = [_given("a funded Account DDA-001")]
            source.interactions = [
                Interaction(
                    when=[_when("the Treasurer submits a Transfer")],
                    then=[_then("a Confirmation Number is returned")],
                )
            ]
            source.is_outline = True
            source.example_rows = [{"amount": "10000 USD"}]
            source.background = [_given("the system is available")]
            source.evidence = ["ref §3"]

            self.target = Scenario("placeholder", 99)
            self.target.translate_from(source)
            self.source = source

        with it(
            "should carry every field from the source "
            "(name, sequentialOrder, storyName, given, interactions, isOutline, exampleRows, background, evidence)"
        ):
            expect(self.target.name).to(equal("Original name"))
            expect(self.target.sequential_order).to(equal(1))
            expect(self.target.story_name).to(equal("My Story"))
            expect(self.target.given[0].text).to(equal("a funded Account DDA-001"))
            expect(self.target.interactions[0].when[0].text).to(
                equal("the Treasurer submits a Transfer")
            )
            expect(self.target.interactions[0].then[0].text).to(
                equal("a Confirmation Number is returned")
            )
            expect(self.target.is_outline).to(be_true)
            expect(self.target.example_rows).to(equal([{"amount": "10000 USD"}]))
            expect(self.target.background[0].text).to(equal("the system is available"))
            expect(self.target.evidence).to(equal(["ref §3"]))

        with context("its interactions"):
            with it(
                "should be a value copy — mutating the source's interactions after "
                "translation should not affect the target"
            ):
                self.source.interactions[0].when.append(_when("extra step"))
                # Target's when list must not grow
                expect(self.target.interactions[0].when).to(have_len(1))

    with context("that carries multiple interactions"):
        with before.each:
            self.scenario = Scenario("multi-interaction", 1)
            self.scenario.given = [_given("initial state")]
            self.scenario.interactions = [
                Interaction(
                    when=[_when("first action")],
                    then=[_then("first outcome"), _then("And second outcome")],
                ),
                Interaction(
                    when=[_when("second action"), _when("And follow-up")],
                    then=[_then("final outcome")],
                ),
            ]

        with it(
            "should expose whenClauses as the flat when-clause list across all "
            "interactions in order"
        ):
            texts = [c.text for c in self.scenario.when_clauses]
            expect(texts).to(equal(["first action", "second action", "And follow-up"]))

        with it(
            "should expose thenClauses as the flat then-clause list across all "
            "interactions in order"
        ):
            texts = [c.text for c in self.scenario.then_clauses]
            expect(texts).to(equal(["first outcome", "And second outcome", "final outcome"]))

        with it(
            "should expose allClauses as given + each interaction's when + then in order"
        ):
            texts = [c.text for c in self.scenario.all_clauses]
            expect(texts).to(
                equal([
                    "initial state",
                    "first action",
                    "first outcome",
                    "And second outcome",
                    "second action",
                    "And follow-up",
                    "final outcome",
                ])
            )

    with context('whose given clauses include an "And " continuation'):
        with before.each:
            self.cont_clause = _given("And the daily Limit is 5000000 USD")
            scenario = Scenario("outline", 1)
            scenario.given = [
                _given("a Treasurer Jane Doe"),
                self.cont_clause,
            ]
            self.scenario = scenario

        with context("the continuation clause"):
            with it("should carry isContinuation true"):
                expect(self.cont_clause.is_continuation).to(be_true)

            with it('should preserve the "And " prefix verbatim in text'):
                expect(self.cont_clause.text).to(
                    equal("And the daily Limit is 5000000 USD")
                )

    with context('whose interaction contains a "But " continuation in its then clauses'):
        with before.each:
            self.but_clause = _then("But the Cart contents are preserved for retry")
            scenario = Scenario("rejection", 1)
            scenario.interactions = [
                Interaction(
                    when=[_when("the Customer submits the Order")],
                    then=[
                        _then("the Order is rejected with reason payment_declined"),
                        self.but_clause,
                    ],
                )
            ]
            self.scenario = scenario

        with context("the continuation clause"):
            with it("should carry isContinuation true"):
                expect(self.but_clause.is_continuation).to(be_true)

            with it('should preserve the "But " prefix verbatim in text'):
                expect(self.but_clause.text).to(
                    equal("But the Cart contents are preserved for retry")
                )
