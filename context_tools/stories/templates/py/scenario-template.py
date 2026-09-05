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
# Pattern: story_test.py extends Mamba with given / when / then — boot in before_all / after_all.

from __future__ import annotations

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import {AggregatePascal}
from story_test import after_all, background, before_all, scenario, story


story("{Story Verb-Noun}", _story)


def _story() -> None:
    {app_camel}: {AppPascal} | None = None
    {aggregate_camel}: {AggregatePascal} | None = None

    def boot() -> None:
        nonlocal {app_camel}
        {app_camel} = {AppPascal}E2e.initialize(config)

    before_all(boot)

    def teardown() -> None:
        if {app_camel}:
            {app_camel}.close()

    after_all(teardown)

    def build_background(given) -> None:
        def background_given() -> None:
            {app_camel}.{background_operation}()

        given("{background given step}", background_given)

        def surface_check(given, when, then) -> None:
            def primary_when() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def observable_outcome() -> None:
                pass  # Assert {observable surface outcome}

            when("{primary when step}", primary_when)
            then("{observable surface outcome}", observable_outcome)

        scenario("{surface check — e.g. rules visible}", surface_check)

        def validation_branch(given, when, then) -> None:
            def primary_when() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def follow_on_when() -> None:
                {aggregate_camel}.{field} = {invalid_value}
                {aggregate_camel}.validate()

            def validation_message() -> None:
                pass  # Assert {validation message on domain object}

            when("{primary when step}", primary_when)
            when("{follow-on when step}", follow_on_when)
            then("{validation message on domain object}", validation_message)

        scenario("{validation branch while typing}", validation_branch)

        def validation_clears(given, when, then) -> None:
            def primary_when() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def prior_invalid_state() -> None:
                {aggregate_camel}.{field} = {invalid_value}
                {aggregate_camel}.validate()

            def corrective_action() -> None:
                {aggregate_camel}.{field} = {valid_value}
                {aggregate_camel}.validate()

            def error_cleared() -> None:
                pass  # Assert {error cleared on domain object}

            when("{primary when step}", primary_when)
            when("{prior invalid state}", prior_invalid_state)
            when("{corrective action}", corrective_action)
            then("{error cleared on domain object}", error_cleared)

        scenario("{validation clears when input conforms}", validation_clears)

        def main_flow(given, when, then) -> None:
            def primary_when() -> None:
                nonlocal {aggregate_camel}
                {aggregate_camel} = {app_camel}.{primary_when_operation}()

            def submit_operation() -> None:
                {aggregate_camel}.{field} = {valid_aggregate_value}
                {aggregate_camel}.{operation}()

            def post_condition() -> None:
                pass  # Assert {post-condition on loaded aggregate}

            when("{primary when step}", primary_when)
            when("{submit operation on domain object}", submit_operation)
            then("{post-condition on loaded aggregate}", post_condition)

        scenario("{main-flow outcome}", main_flow)

    background(build_background)
