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
#     examples/                          # epic-shared ExampleFactory values (when shared)
#     givens.py                          # epic-shared background Given helpers
#     whens.py                           # epic-shared When helpers (when shared)
#     {sub-epic-verb-noun}/              # omit this level when the story file lives under epic/
#       examples/{topic}_examples.py     # lowest shared folder for this story's fixtures
#       givens.py                        # background Given helpers for this sub-epic/story
#       whens.py                         # When helpers for this sub-epic/story
#       {story_snake_slug}.{tier}.py     # story file — one GWT file per story per tier
#
# # Shared helper (copy once per tests/ tree — full source inlined below)
# story_test: tests/story_test.py
#
# # Naming rules
# - Epic / SubEpic folders → kebab-case verb-noun (Sign Up → sign-up)
# - Story test file        → {story_snake_slug}.{tier}.py at epic or sub-epic — NO {story}/ folder
# - Tier                   → file extension segment (.e2e.py, .front-end.py, .back-end.py)
# - Examples module        → examples/{topic}_examples.py (concrete values, not inline in GWT)
# - Epic helper (py only)  → {epic_snake}_helper.py — sole snake_case naming exception
# - Forbidden              → {story}/ folders, *_story.*, *_test_helper.* splits
# ```
#
# Pattern: sign-up-create-account.e2e.ts — same story_test API as story-test.ts.

from __future__ import annotations

from expects import be_none, equal, expect

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
from story_test import ScenarioSteps, after_all, background, before_all, scenario, story
from whens import {primary_when_fn}


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
        given("{background given step}", lambda: {background_given_fn}({app_camel}))

        def validation_branch(steps: ScenarioSteps) -> None:
            steps.when("{primary when step}", lambda: _primary_when()).and_(
                "{follow-on when step}",
                lambda: _invalid_input(),
            )
            steps.then("{validation message on domain object}", lambda: _expect_error())

        scenario("{validation branch while typing}", validation_branch)

        def validation_clears(steps: ScenarioSteps) -> None:
            steps.when("{primary when step}", lambda: _primary_when()).and_(
                "{prior invalid state}",
                lambda: _invalid_input(),
            )
            steps.when("{corrective action}", lambda: _valid_input())
            steps.then("{error cleared on domain object}", lambda: _expect_cleared())

        scenario("{validation clears when input conforms}", validation_clears)

        def main_flow(steps: ScenarioSteps) -> None:
            steps.when("{primary when step}", lambda: _primary_when())
            steps.when("{submit operation on domain object}", lambda: _submit())
            steps.then("{post-condition on loaded aggregate}", lambda: _expect_state())

        scenario("{main-flow outcome}", main_flow)

    background(shared)

    def _primary_when() -> None:
        nonlocal {aggregate_camel}
        {aggregate_camel} = {primary_when_fn}({app_camel})

    def _invalid_input() -> None:
        assert {aggregate_camel} is not None
        {aggregate_camel}.{field} = invalid_{field}_example
        {aggregate_camel}.validate()

    def _valid_input() -> None:
        assert {aggregate_camel} is not None
        {aggregate_camel}.{field} = valid_{field}_example
        {aggregate_camel}.validate()

    def _submit() -> None:
        assert {aggregate_camel} is not None
        {aggregate_camel}.{field} = valid_{aggregate}_example.{field}
        {aggregate_camel}.{operation}()

    def _expect_error() -> None:
        assert {aggregate_camel} is not None
        expect({aggregate_camel}.errors.{field}).to(equal({ERROR_CONSTANT}_MESSAGE))

    def _expect_cleared() -> None:
        assert {aggregate_camel} is not None
        expect({aggregate_camel}.errors.{field}).to(be_none)

    def _expect_state() -> None:
        assert {app_camel} is not None and {aggregate_camel} is not None
        {entity_camel} = {app_camel}.{repository}().load({aggregate_camel})
        expect({entity_camel}.is_at_{state}("{StateName}")).to(equal(True))


story("{Story Verb-Noun}", _{story_snake_slug}_story)
