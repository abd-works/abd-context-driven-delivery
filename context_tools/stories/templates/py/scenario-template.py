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
# examples:  tests/{epic-verb-noun}/{sub-epic-verb-noun}/examples/{story_verb_noun}_examples.py
# givens:    tests/{epic-verb-noun}/{sub-epic-verb-noun}/givens.py
# whens:     tests/{epic-verb-noun}/{sub-epic-verb-noun}/whens.py
# ```
#
# Pattern: mirror sign-up-create-account.e2e.ts (Mamba/RSpec via story_test).

from __future__ import annotations

from expects import be_none, equal, expect
from mamba import after, before, description

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import (
    {AggregatePascal},
    {ERROR_CONSTANT}_MESSAGE,
)
from examples.{story_verb_noun}_examples import (
    invalid_{field}_example,
    valid_{aggregate}_example,
    valid_{field}_example,
)
from givens import {background_given_fn}
from story_test import background, scenario, story
from whens import {primary_when_fn}


with description("{Story Verb-Noun}") as story_ctx:
    story_ctx.{app_camel}: {AppPascal} | None = None
    story_ctx.{aggregate_camel}: {AggregatePascal} | None = None

    with before.all:
        def _boot() -> None:
            story_ctx.{app_camel} = {AppPascal}E2e.initialize(config)

    with after.all:
        def _shutdown() -> None:
            if story_ctx.{app_camel} is not None:
                story_ctx.{app_camel}.close()

    def _story_body() -> None:
        def _background(given):  # type: ignore[no-untyped-def]
            given("{background given step}", lambda: {background_given_fn}(story_ctx.{app_camel}))

            def _validation_branch(steps):  # type: ignore[no-untyped-def]
                when, then = steps["when"], steps["then"]

                when("{primary when step}", lambda: _primary_when())
                when("{follow-on when step}", lambda: _invalid_input())
                then("{validation message on domain object}", lambda: expect(
                    story_ctx.{aggregate_camel}.errors.{field}
                ).to(equal({ERROR_CONSTANT}_MESSAGE)))

            scenario("{validation branch while typing}", _validation_branch)

            def _clears_when_valid(steps):  # type: ignore[no-untyped-def]
                when, then = steps["when"], steps["then"]

                (
                    when("{primary when step}", lambda: _primary_when())
                    .and_("{prior invalid state}", lambda: _invalid_input())
                )
                when("{corrective action}", lambda: _valid_input())
                then("{error cleared on domain object}", lambda: expect(
                    story_ctx.{aggregate_camel}.errors.{field}
                ).to(be_none))

            scenario("{validation clears when input conforms}", _clears_when_valid)

            def _main_flow(steps):  # type: ignore[no-untyped-def]
                when, then = steps["when"], steps["then"]

                when("{primary when step}", lambda: _primary_when())
                when("{submit operation on domain object}", lambda: _submit())
                then("{post-condition on loaded aggregate}", lambda: _expect_state())

            scenario("{main-flow outcome}", _main_flow)

        background(_background)

    def _primary_when() -> None:
        story_ctx.{aggregate_camel} = {primary_when_fn}(story_ctx.{app_camel})

    def _invalid_input() -> None:
        creds = story_ctx.{aggregate_camel}
        creds.{field} = invalid_{field}_example
        creds.validate()

    def _valid_input() -> None:
        creds = story_ctx.{aggregate_camel}
        creds.{field} = valid_{field}_example
        creds.validate()

    def _submit() -> None:
        creds = story_ctx.{aggregate_camel}
        creds.{field} = valid_{aggregate}_example.{field}
        creds.{operation}()

    def _expect_state() -> None:
        {entity_camel} = story_ctx.{app_camel}.{repository}().load(story_ctx.{aggregate_camel})
        expect({entity_camel}.is_at_{state}("{StateName}")).to(equal(True))

    story("{Story Verb-Noun}", _story_body)
