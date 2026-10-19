"""Mamba spec for `a Markdown document`. Mirrors `## Documents` in ../../bdd-context.md."""

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
for _candidate in _HERE.parents:
    if (_candidate / "practices" / "stories" / "src" / "practices" / "stories").is_dir():
        if str(_candidate) not in sys.path:
            sys.path.insert(0, str(_candidate))
        break

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error

from practices.stories.model.story_model import Epic, Story, StoryType, Epic
from practices.stories.model.story_model import Scenario
from practices.stories.model.story_model import StoryModel
from practices.stories.model.markdown.nodes import (
    MarkdownParseError,
    MarkdownStoryModel,
)


class SpecFixture:
    def canonical_story_map_4_epics_3_epics(self) -> StoryModel:
        story_map = StoryModel()
        for i in range(1, 5):
            epic = Epic(f"Epic {i}", i)
            story_map.epics.append(epic)
        first = story_map.epics[0]
        for j in range(1, 4):
            sub = Epic(f"Epic 1.{j}", j)
            story = Story(f"Story {j}", 1, StoryType.USER)
            story.scenarios.append(
                Scenario(name=f"AC text {j}.1", sequential_order=1)
            )
            sub.stories.append(story)
            first.epics.append(sub)
        return story_map


fixture = SpecFixture()


with description("a Markdown document") as self:
    with before.each:
        self.markdown = MarkdownStoryModel()

    with it("should contain no headings"):
        empty_story_map = StoryModel()
        text = self.markdown.render(empty_story_map)
        expect(text.count("#")).to(equal(0))

    with context(
        "that holds a rendered Story Map with 4 Epics and 3 Epics under the first Epic"
    ):
        with before.each:
            self.source = fixture.canonical_story_map_4_epics_3_epics()
            self.text = self.markdown.render(self.source)

        with it("should contain 4 top-level headings"):
            top_headings = [
                line for line in self.text.splitlines() if line.startswith("# ")
            ]
            expect(top_headings).to(have_len(4))

        with it("should contain 3 second-level headings under the first top-level heading"):
            lines = self.text.splitlines()
            first_index = next(i for i, l in enumerate(lines) if l.startswith("# "))
            next_top_index = next(
                (
                    i
                    for i in range(first_index + 1, len(lines))
                    if lines[i].startswith("# ")
                ),
                len(lines),
            )
            second_headings = [
                l
                for l in lines[first_index + 1 : next_top_index]
                if l.startswith("## ")
            ]
            expect(second_headings).to(have_len(3))

        with it("should list every Story as a bullet under its Epic"):
            lines = self.text.splitlines()
            story_bullets = [l for l in lines if l.startswith("- ")]
            expect(story_bullets).to(have_len(3))

        with it("should list every Scenario as an indented bullet under its Story"):
            lines = self.text.splitlines()
            ac_bullets = [l for l in lines if l.startswith("  - ")]
            expect(ac_bullets).to(have_len(3))

        with it("should preserve the sequential order of every node"):
            lines = self.text.splitlines()
            first_four_top = [l for l in lines if l.startswith("# ")][:4]
            names = [line.removeprefix("# ") for line in first_four_top]
            expect(names).to(equal(["Epic 1", "Epic 2", "Epic 3", "Epic 4"]))

        with context(
            "with a fifth Epic appended in the source Story Map and re-rendered"
        ):
            with before.each:
                self.source.append_epic(Epic("Epic 5", 5))
                self.new_text = self.markdown.render(self.source)

            with it("should contain 5 top-level headings"):
                top_headings = [
                    l for l in self.new_text.splitlines() if l.startswith("# ")
                ]
                expect(top_headings).to(have_len(5))

            with context("the first 4 headings"):
                with it("should be unchanged"):
                    prev_top = [
                        l for l in self.text.splitlines() if l.startswith("# ")
                    ]
                    new_top = [
                        l for l in self.new_text.splitlines() if l.startswith("# ")
                    ]
                    expect(new_top[:4]).to(equal(prev_top))

        with context(
            "with the first Epic removed in the source Story Map and re-rendered"
        ):
            with before.each:
                self.source.epics.pop(0)
                self.new_text = self.markdown.render(self.source)

            with it("should contain 3 top-level headings"):
                top_headings = [
                    l for l in self.new_text.splitlines() if l.startswith("# ")
                ]
                expect(top_headings).to(have_len(3))

            with context("the headings for the removed Epic and its descendants"):
                with it("should be absent"):
                    expect("# Epic 1" in self.new_text).to(be_false)
                    expect("Epic 1.1" in self.new_text).to(be_false)

        with context(
            "with the first Epic renamed in the source Story Map and re-rendered"
        ):
            with before.each:
                self.source.epics[0].name = "Epic 1 (renamed)"
                self.new_text = self.markdown.render(self.source)

            with context("the first heading"):
                with it("should carry the new name"):
                    first_heading = next(
                        l for l in self.new_text.splitlines() if l.startswith("# ")
                    )
                    expect(first_heading).to(equal("# Epic 1 (renamed)"))

            with context("the headings under it"):
                with it("should be unchanged"):
                    expect("## Epic 1.1" in self.new_text).to(be_true)
                    expect("## Epic 1.2" in self.new_text).to(be_true)
                    expect("## Epic 1.3" in self.new_text).to(be_true)

    with context("that is being read back into a MarkdownStoryModel"):
        with before.each:
            self.source = fixture.canonical_story_map_4_epics_3_epics()
            self.text = self.markdown.render(self.source)
            self.reconstructed = self.markdown.parse(self.text)

        with context("the reconstructed Story Map"):
            with it(
                "should hold every Epic, Epic, Story, and Scenario in sequential order"
            ):
                expect(self.reconstructed.epics).to(have_len(4))
                first_epic = self.reconstructed.epics[0]
                expect(first_epic.epics).to(have_len(3))
                expect(first_epic.epics[0].stories).to(have_len(1))
                expect(first_epic.epics[0].stories[0].scenarios).to(
                    have_len(1)
                )

    with context("that includes metadata and prose around valid story structure"):
        with before.each:
            self.document = """# Story Map - Sample

**Actors:** Customer, System
_Scope: mixed markdown content should be tolerated._

## Checkout
- Redeem voucher
  - voucher is valid

## Context Gaps
- this bullet should be ignored because it is not under a story node
"""
            self.reconstructed = self.markdown.parse(self.document)

        with it("should ignore non-structural lines and still parse the story map"):
            expect(self.reconstructed.epics).to(have_len(1))
            expect(self.reconstructed.epics[0].epics).to(have_len(1))
            checkout = self.reconstructed.epics[0].epics[0]
            expect(checkout.name).to(equal("Checkout"))
            expect(checkout.stories).to(have_len(1))
            expect(checkout.stories[0].scenarios).to(have_len(1))

    with context("that uses `(E)/(S)` outline notation"):
        with before.each:
            self.document = """# Story Map - pml-my

**Actors:** Customer, System

(E) Authenticate
    (E) Sign In
        (S) Self-Care Customer --> View Sign-In Form
        (S) Self-Care Customer --> Submit Sign-In Credentials

## Context Gaps
- prose bullets should be ignored in outline mode
"""
            self.reconstructed = self.markdown.parse(self.document)

        with it("should parse Epics, Epics, and Stories from outline lines"):
            expect(self.reconstructed.epics).to(have_len(1))
            expect(self.reconstructed.epics[0].name).to(equal("Authenticate"))
            expect(self.reconstructed.epics[0].epics).to(have_len(1))
            sign_in = self.reconstructed.epics[0].epics[0]
            expect(sign_in.name).to(equal("Sign In"))
            expect(sign_in.stories).to(have_len(2))
            expect(sign_in.stories[0].name).to(equal("View Sign-In Form"))
            expect(sign_in.stories[1].name).to(equal("Submit Sign-In Credentials"))

    with context("that hangs outline stories directly under an Epic"):
        with before.each:
            self.document = """# Story Map

(E) Resolve Check
    (S) Player --> Make Trait Check
    (S) Player --> Oppose Check
"""
            self.reconstructed = self.markdown.parse(self.document)

        with it("should synthesize a Epic so stories are not dropped"):
            epic = self.reconstructed.epics[0]
            expect(epic.name).to(equal("Resolve Check"))
            expect(epic.epics).to(have_len(1))
            expect(epic.epics[0].stories).to(have_len(2))
            expect(epic.epics[0].stories[0].name).to(equal("Make Trait Check"))
            expect(epic.epics[0].stories[1].name).to(equal("Oppose Check"))

    with context("that uses outline estimate lines"):
        with before.each:
            self.document = """# Story Map - Treasury

(E) Move money
    * approx 22-27 total stories
    (E) Compose transfer
        (S) Treasurer --> Draft transfer details
        * approx 2-3 more stories (validation and entry)
    (E) Track transfer
        * approx 2-3 more stories (status views)
"""
            self.reconstructed = self.markdown.parse(self.document)

        with it("should attach estimates to epics and sub-epics"):
            epic = self.reconstructed.epics[0]
            expect(epic.estimate).to(equal("approx 22-27 total stories"))
            compose = epic.epics[0]
            expect(compose.estimate).to(equal("approx 2-3 more stories (validation and entry)"))
            track = epic.epics[1]
            expect(track.estimate).to(equal("approx 2-3 more stories (status views)"))
            expect(track.stories).to(have_len(0))

        with it("should round-trip estimates when re-rendered as outline"):
            text = self.markdown.render(self.reconstructed)
            round_trip = self.markdown.parse(text)
            expect(round_trip.epics[0].estimate).to(equal("approx 22-27 total stories"))
            expect(round_trip.epics[0].epics[0].estimate).to(
                equal("approx 2-3 more stories (validation and entry)")
            )

    with context("that uses heading-style stories and numbered acceptance criteria"):
        with before.each:
            self.document = """# Acceptance Criteria - Full Application

## Authenticate
### Sign In
#### Submit Sign-In Credentials
1. **WHEN** valid credentials are submitted
2. **WHEN** unverified email signs in
"""
            self.reconstructed = self.markdown.parse(self.document)

        with it("should parse deep headings as Story nodes and numbered lines as Scenarios"):
            authenticate = self.reconstructed.epics[0]
            sign_in = authenticate.epics[0]
            expect(sign_in.stories).to(have_len(1))
            story = sign_in.stories[0]
            expect(story.name).to(equal("Submit Sign-In Credentials"))
            expect(story.scenarios).to(have_len(2))

    with context("that is not a valid Markdown story map"):
        with context("the read"):
            with it("should be rejected"):
                bad_document = "this is not markdown\nno headings\njust prose"
                expect(lambda: self.markdown.parse(bad_document)).to(
                    raise_error(MarkdownParseError)
                )
