# ---
# fidelity: [specification, engineering]
# artifact: [story-scenarios]
# format: py
# ---
#
# Scenario template — refer to context_tools/language-tools.md for tooling.
#
# ```
# # Params — fill before writing code
# epic:       {epic-verb-noun}           # kebab folder under tests/
# sub_epic:   {sub-epic-verb-noun}       # kebab folder under epic/ (omit level if story hangs off epic)
# story:      {story-verb-noun}          # Verb Noun title from the story map
# story_file: {story_snake_slug}         # snake file slug, e.g. sign_up_create_account
# tier:       e2e | front-end | back-end | {system}
#
# # Artifact layout (artifacts-mirror-story-hierarchy)
# tests/
#   {epic-verb-noun}/
#     {sub-epic-verb-noun}/              # omit when the story file lives under epic/
#       {story_snake_slug}.{tier}.py     # one GWT file per story per tier
#
# # Machinery (copy once per tests/ tree — full source inlined below)
# story_test: tests/story_test.py
#
# # Naming rules
# - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
# - Story test file        → {story_snake_slug}.{tier}.py at epic or sub-epic — NO {story}/ folder
# - Tier                   → file extension segment (.e2e.py, .front-end.py, .back-end.py)
# - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
# ```
#
# Pattern: same API and shape as scenario-template.ts.

from __future__ import annotations

from expects import be_above, be_none, equal, expect

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import (
    {AggregatePascal},
    {ERROR_CONSTANT}_MESSAGE,
)
from story_test import after_all, background, before_all, scenario, story


def _{story_snake_slug}_story() -> None:
    {app_camel}: {AppPascal} | None = None
    {aggregate_camel}: {AggregatePascal} | None = None

    before_all(lambda: _boot())
    after_all(lambda: _shutdown())

    def _boot() -> None:
        nonlocal {app_camel}
        {app_camel} = {AppPascal}E2e.initialize(config)

    def _shutdown() -> None:
        nonlocal {app_camel}
        if {app_camel} is not None:
            {app_camel}.close()

    background(_shared_background)

    def _shared_background(given) -> None:
        given(
            "{background given step}",
            lambda: {app_camel}.{background_operation}(),
        )

        scenario("{surface check — e.g. rules visible}", _surface_check)
        scenario("{validation branch while typing}", _validation_branch)
        scenario("{validation clears when input conforms}", _validation_clears)
        scenario("{main-flow outcome}", _main_flow)

    def _surface_check(when, then) -> None:
        nonlocal {aggregate_camel}

        def _when_primary() -> None:
            nonlocal {aggregate_camel}
            {aggregate_camel} = {app_camel}.{primary_when_operation}()

        when("{primary when step}", _when_primary)
        then(
            "{observable surface outcome}",
            lambda: (
                setattr({aggregate_camel}, "{field}", ""),
                {aggregate_camel}.validate(),
                expect(len({aggregate_camel}.errors.{field})).to(be_above(0)),
            )[2],
        )

    def _validation_branch(when, then) -> None:
        nonlocal {aggregate_camel}

        def _when_primary() -> None:
            nonlocal {aggregate_camel}
            {aggregate_camel} = {app_camel}.{primary_when_operation}()

        def _when_invalid() -> None:
            {aggregate_camel}.{field} = {invalid_value}
            {aggregate_camel}.validate()

        when("{primary when step}", _when_primary).and_("{follow-on when step}", _when_invalid)
        then(
            "{validation message on domain object}",
            lambda: expect({aggregate_camel}.errors.{field}).to(equal({ERROR_CONSTANT}_MESSAGE)),
        )

    def _validation_clears(when, then) -> None:
        nonlocal {aggregate_camel}

        def _when_primary() -> None:
            nonlocal {aggregate_camel}
            {aggregate_camel} = {app_camel}.{primary_when_operation}()

        def _when_invalid() -> None:
            {aggregate_camel}.{field} = {invalid_value}
            {aggregate_camel}.validate()

        def _when_valid() -> None:
            {aggregate_camel}.{field} = {valid_value}
            {aggregate_camel}.validate()

        when("{primary when step}", _when_primary).and_("{prior invalid state}", _when_invalid)
        when("{corrective action}", _when_valid)
        then(
            "{error cleared on domain object}",
            lambda: expect({aggregate_camel}.errors.{field}).to(be_none),
        )

    def _main_flow(when, then) -> None:
        nonlocal {aggregate_camel}

        def _when_primary() -> None:
            nonlocal {aggregate_camel}
            {aggregate_camel} = {app_camel}.{primary_when_operation}()

        def _when_submit() -> None:
            {aggregate_camel}.{field} = {valid_aggregate_value}
            {aggregate_camel}.{operation}()

        when("{primary when step}", _when_primary)
        when("{submit operation on domain object}", _when_submit)
        then(
            "{post-condition on loaded aggregate}",
            lambda: expect(
                {app_camel}.{repository}().load({aggregate_camel}).is_at_{state}('{StateName}')
            ).to(equal(True)),
        )


story("{Story Verb-Noun}", _{story_snake_slug}_story)
