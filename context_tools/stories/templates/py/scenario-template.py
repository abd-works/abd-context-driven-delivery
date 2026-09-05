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
# Pattern: story_test machinery only — lifecycle, background(), scenario(), inline step bodies.

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

    def boot() -> None:
        nonlocal {app_camel}
        {app_camel} = {AppPascal}E2e.initialize(config)

    def shutdown() -> None:
        nonlocal {app_camel}
        if {app_camel} is not None:
            {app_camel}.close()

    before_all(boot)
    after_all(shutdown)

    def shared(given) -> None:
        given(
            "{background given step}",
            lambda: {app_camel}.{background_operation}(),
        )

        def surface_check(steps) -> None:
            def when_primary() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def surface_then() -> None:
                assert {aggregate_camel} is not None
                {aggregate_camel}.{field} = ""
                {aggregate_camel}.validate()
                expect(len({aggregate_camel}.errors.{field})).to(be_above(0))

            steps.when("{primary when step}", when_primary)
            steps.then("{observable surface outcome}", surface_then)

        scenario("{surface check — e.g. rules visible}", surface_check)

        def validation_branch(steps) -> None:
            def when_primary() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def when_invalid() -> None:
                {aggregate_camel}.{field} = {invalid_value}
                {aggregate_camel}.validate()

            steps.when("{primary when step}", when_primary).and_(
                "{follow-on when step}",
                when_invalid,
            )
            steps.then(
                "{validation message on domain object}",
                lambda: expect({aggregate_camel}.errors.{field}).to(
                    equal({ERROR_CONSTANT}_MESSAGE)
                ),
            )

        scenario("{validation branch while typing}", validation_branch)

        def validation_clears(steps) -> None:
            def when_primary() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def when_invalid() -> None:
                {aggregate_camel}.{field} = {invalid_value}
                {aggregate_camel}.validate()

            def when_valid() -> None:
                {aggregate_camel}.{field} = {valid_value}
                {aggregate_camel}.validate()

            steps.when("{primary when step}", when_primary).and_(
                "{prior invalid state}",
                when_invalid,
            )
            steps.when("{corrective action}", when_valid)
            steps.then(
                "{error cleared on domain object}",
                lambda: expect({aggregate_camel}.errors.{field}).to(be_none),
            )

        scenario("{validation clears when input conforms}", validation_clears)

        def main_flow(steps) -> None:
            def when_primary() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def when_submit() -> None:
                {aggregate_camel}.{field} = {valid_aggregate_value}
                {aggregate_camel}.{operation}()

            steps.when("{primary when step}", when_primary)
            steps.when("{submit operation on domain object}", when_submit)
            steps.then(
                "{post-condition on loaded aggregate}",
                lambda: expect(
                    {app_camel}.{repository}().load({aggregate_camel}).is_at_{state}(
                        "{StateName}"
                    )
                ).to(equal(True)),
            )

        scenario("{main-flow outcome}", main_flow)

    background(shared)


story("{Story Verb-Noun}", _{story_snake_slug}_story)
