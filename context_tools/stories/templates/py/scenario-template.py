# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenario template — refer to context_tools/language-tools.md for tooling.
#
# ```
# epic:      {epic-verb-noun}
# sub_epic:  {sub-epic-verb-noun}
# story:     {story-verb-noun}
# file:      tests/{epic-verb-noun}/{sub-epic-verb-noun}/{story_verb_noun}.{tier}.py
# tier:      front-end | back-end | external-system
# fixtures:  tests/{epic-verb-noun}/examples/  tests/{epic-verb-noun}/{sub-epic-verb-noun}/givens.py
# ```
#
# Pattern: mirror sign-up-create-account.e2e.ts — Mamba describe/context/it (RSpec-style);
# domain ops in When; observable expects in Then/And; infrastructure in before.all;
# shared state on StoryScenario subclass.

from __future__ import annotations

from expects import equal, expect
from mamba import before, context, description, it

from domain.{bounded_context}.{app_snake} import {AppPascal}
from story_test import StoryScenario


class {StoryPascal}Story(StoryScenario[{AppPascal}]):
    """Shared boot, background, and typed handles for this story's scenarios."""

    {aggregate_camel}: {AggregatePascal}

    @classmethod
    def boot(cls) -> {AppPascal}:
        """Infrastructure only (browser, config, wiring). Never domain assertions here."""
        return {AppPascal}.initialize()  # config from examples/

    def background(self) -> None:
        """Background — shared Given state every scenario inherits. Domain state only."""
        self.{aggregate_camel} = self.app.{aggregate_camel}()


with description("{Story Verb-Noun}") as self:
    with before.all:
        self.ctx = {StoryPascal}Story()
        self.ctx.app = {StoryPascal}Story.boot()
        self.ctx.background()

    with context("{main-flow outcome}"):
        with before.each:
            def _given_and_when() -> None:
                # Given {given step text}
                ...
                # When {when step text} — domain operation, e.g. self.ctx.app.authentication().register(...)
                ...

            _given_and_when()

        with it("Then {then step text}"):
            expect(self.ctx.{aggregate_camel}.{observable}()).to(equal(/* expected */))

        with it("{additional outcome}"):
            expect(self.ctx.{aggregate_camel}.{observable2}()).to(equal(/* expected */))

    with context("{alternate outcome — e.g. validation branch}"):
        with before.each:
            def _given_and_when() -> None:
                # Given {alternate given}
                ...
                # When {alternate when}
                ...

            _given_and_when()

        with it("Then {alternate then}"):
            expect(/* observable */).to(equal(/* expected */))
