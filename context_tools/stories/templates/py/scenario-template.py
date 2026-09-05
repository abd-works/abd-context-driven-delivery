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
# Pattern: normal code inline under each with — same steps as scenario-template.ts.

from __future__ import annotations

from expects import be_above, be_none, equal, expect
from mamba import after, before

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import (
    {AggregatePascal},
    {ERROR_CONSTANT}_MESSAGE,
)
from story_test import and_, background, given, scenario, story, then, when


with story("{Story Verb-Noun}"):
    with before.all:
        self.{app_camel} = {AppPascal}E2e.initialize(config)

    with after.all:
        if self.{app_camel}:
            self.{app_camel}.close()

    with background.each:
        with given("{background given step}"):
            self.{app_camel}.{background_operation}()

        with scenario("{surface check — e.g. rules visible}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with then("{observable surface outcome}"):
                self.{aggregate_camel}.{field} = ""
                self.{aggregate_camel}.validate()
                expect(len(self.{aggregate_camel}.errors.{field})).to(be_above(0))

        with scenario("{validation branch while typing}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with and_("{follow-on when step}"):
                self.{aggregate_camel}.{field} = {invalid_value}
                self.{aggregate_camel}.validate()

            with then("{validation message on domain object}"):
                expect(self.{aggregate_camel}.errors.{field}).to(
                    equal({ERROR_CONSTANT}_MESSAGE)
                )

        with scenario("{validation clears when input conforms}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with and_("{prior invalid state}"):
                self.{aggregate_camel}.{field} = {invalid_value}
                self.{aggregate_camel}.validate()

            with when("{corrective action}"):
                self.{aggregate_camel}.{field} = {valid_value}
                self.{aggregate_camel}.validate()

            with then("{error cleared on domain object}"):
                expect(self.{aggregate_camel}.errors.{field}).to(be_none)

        with scenario("{main-flow outcome}"):
            with when("{primary when step}"):
                self.{aggregate_camel} = self.{app_camel}.{primary_when_operation}()

            with when("{submit operation on domain object}"):
                self.{aggregate_camel}.{field} = {valid_aggregate_value}
                self.{aggregate_camel}.{operation}()

            with then("{post-condition on loaded aggregate}"):
                loaded = (
                    self.{app_camel}
                    .{repository}()
                    .load(self.{aggregate_camel})
                )
                expect(loaded.is_at_{state}("{StateName}")).to(equal(True))
