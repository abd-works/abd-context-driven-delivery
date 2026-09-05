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
# Pattern: story_test machinery only — inline lambdas in given/when/then (same as story-test.ts).

from __future__ import annotations

from expects import be_above, be_none, equal, expect

from domain.{bounded_context}.runtime import {AppPascal}E2e, config
from domain.{bounded_context}.{aggregate_snake} import (
    {AggregatePascal},
    {ERROR_CONSTANT}_MESSAGE,
)
from story_test import after_all, background, before_all, scenario, story


def _{story_snake_slug}_story() -> None:
    {app_camel}: list[{AppPascal} | None] = [None]
    {aggregate_camel}: list[{AggregatePascal} | None] = [None]

    before_all(lambda: {app_camel}.__setitem__(0, {AppPascal}E2e.initialize(config)))
    after_all(lambda: {app_camel}[0] and {app_camel}[0].close())

    background(
        lambda given: (
            given(
                "{background given step}",
                lambda: {app_camel}[0].{background_operation}(),
            ),
            scenario(
                "{surface check — e.g. rules visible}",
                lambda when, then: (
                    when(
                        "{primary when step}",
                        lambda: {aggregate_camel}.__setitem__(
                            0, {app_camel}[0].{primary_when_operation}()
                        ),
                    ),
                    then(
                        "{observable surface outcome}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", ""),
                            {aggregate_camel}[0].validate(),
                            expect(len({aggregate_camel}[0].errors.{field})).to(be_above(0)),
                        )[2],
                    ),
                ),
            ),
            scenario(
                "{validation branch while typing}",
                lambda when, then: (
                    when(
                        "{primary when step}",
                        lambda: {aggregate_camel}.__setitem__(
                            0, {app_camel}[0].{primary_when_operation}()
                        ),
                    ).and_(
                        "{follow-on when step}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", {invalid_value}),
                            {aggregate_camel}[0].validate(),
                        )
                        and None,
                    ),
                    then(
                        "{validation message on domain object}",
                        lambda: expect({aggregate_camel}[0].errors.{field}).to(
                            equal({ERROR_CONSTANT}_MESSAGE)
                        ),
                    ),
                ),
            ),
            scenario(
                "{validation clears when input conforms}",
                lambda when, then: (
                    when(
                        "{primary when step}",
                        lambda: {aggregate_camel}.__setitem__(
                            0, {app_camel}[0].{primary_when_operation}()
                        ),
                    ).and_(
                        "{prior invalid state}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", {invalid_value}),
                            {aggregate_camel}[0].validate(),
                        )
                        and None,
                    ),
                    when(
                        "{corrective action}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", {valid_value}),
                            {aggregate_camel}[0].validate(),
                        )
                        and None,
                    ),
                    then(
                        "{error cleared on domain object}",
                        lambda: expect({aggregate_camel}[0].errors.{field}).to(be_none),
                    ),
                ),
            ),
            scenario(
                "{main-flow outcome}",
                lambda when, then: (
                    when(
                        "{primary when step}",
                        lambda: {aggregate_camel}.__setitem__(
                            0, {app_camel}[0].{primary_when_operation}()
                        ),
                    ),
                    when(
                        "{submit operation on domain object}",
                        lambda: (
                            setattr({aggregate_camel}[0], "{field}", {valid_aggregate_value}),
                            {aggregate_camel}[0].{operation}(),
                        )
                        and None,
                    ),
                    then(
                        "{post-condition on loaded aggregate}",
                        lambda: expect(
                            {app_camel}[0]
                            .{repository}()
                            .load({aggregate_camel}[0])
                            .is_at_{state}("{StateName}")
                        ).to(equal(True)),
                    ),
                ),
            ),
        )
        or None,
    )


story("{Story Verb-Noun}", _{story_snake_slug}_story)
