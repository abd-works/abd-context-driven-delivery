# ---
# fidelity: [implementation]
# artifact: [story-acceptance-tests]
# format: py
# ---
#
# Acceptance tests template (Python) — refer to cdd_guidance/references/language-tools.md for tooling.
#
# A story test is its scenarios file in code with every step's body filled in: each Given seeds state through its
# real owner, each When calls the domain operation it tests, each Then asserts what the product answered. The files
# this fidelity writes, one shape each below:
#
# ```
# story_tests/{epic}/{sub-epic}/
#   {story}/{story_snake}_story.test.py          # one story, run on its own (FILE 1)
#   {sub_epic_slug}.story.shared.py              # scenarios every tier replays (FILE 2)
#   {sub_epic_slug}.story.domain.spec.py         # the shared scenarios on the domain objects (FILE 3)
#   {sub_epic_slug}.story.server.spec.py         # the same scenarios through the server (FILE 3, other tier)
# {module}/{concept}_examples.py                 # named examples, beside the code they build (FILE 4)
#
# # Machinery — copy once per tests tree if missing:
#   practices/stories/templates/py/story_test.py → tests/story_test.py
# ```
#
# Write a story as FILE 1 when one tier proves it; write FILES 2 and 3 when the sub-epic's stories run at more than
# one tier, so each tier replays one copy of the steps. Python examples sit beside the code they build, because a
# story folder's name holds hyphens, which no Python import can name.

# FILE 1: story_tests/{epic}/{sub-epic}/{story}/{story_snake}_story.test.py
from expects import equal, expect

from story_test import given, scenario, story, then, when
from {module}.{concept}_examples import {EXAMPLE}, seed_{example}
from {module}.{family_slug} import {ClassName}Repository, {DomainRefusal}

with story("{Story Verb–Noun}"):
    with scenario("{actor} {does the main flow}"):
        with given("{the state the scenario starts from}"):
            self.repository = seed_{example}({ClassName}Repository())
        with when("{actor} {does the action}"):
            self.answer = self.repository.load({EXAMPLE}.identity).{operation}({EXAMPLE}.value)
        with then("{the outcome a person can check}"):
            expect(self.answer.{property}).to(equal({EXAMPLE}.expected))

    with scenario("{actor} {does the action} {in the edge or error case}"):
        with given("{the state of that case}"):
            self.repository = seed_{example}({ClassName}Repository())
        with when("{actor} {does the action}"):
            self.refusal = {DomainRefusal}.raised_by(lambda: self.repository.load({EXAMPLE}.identity).{operation}(None))
        with then("{the refusal names what was refused}"):
            expect(self.refusal.value).to(equal(None))


# FILE 2: story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.shared.py
# Steps reach the product only through the world a tier hands them, so every tier replays the same steps.
def {story_snake}(world) -> None:
    with story("{Story Verb–Noun}"):
        with scenario("{actor} {does the main flow}"):
            with given("{the state the scenario starts from}"):
                world.seed({EXAMPLE})
            with when("{actor} {does the action}"):
                world.answer = world.{ClassName}.load({EXAMPLE}.identity).{operation}({EXAMPLE}.value)
            with then("{the outcome a person can check}"):
                expect(world.answer.{property}).to(equal({EXAMPLE}.expected))


# FILE 3: story_tests/{epic}/{sub-epic}/{sub_epic_slug}.story.domain.spec.py (server: .story.server.spec.py)
# The tier names its world: the domain objects themselves, or the same operations through the server.
from {sub_epic_slug}_story_shared import {story_snake}
from {module}.{tier}_world import {Tier}World

{story_snake}({Tier}World())


# FILE 4: {module}/{concept}_examples.py — one named example for each example the scenarios name.
{EXAMPLE} = {ClassName}Example(identity="{id}", value="{value}", expected="{expected}")


def seed_{example}(repository: {ClassName}Repository) -> {ClassName}Repository:
    """Seed state at its real owner: the repository, or the external system's test adapter beneath it."""
    repository.create({EXAMPLE}.identity, {EXAMPLE}.value)
    return repository
