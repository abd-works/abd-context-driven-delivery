"""Mamba spec for `a Markdown document`. Mirrors `## Documents` in bdd-context.md."""

import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(_HERE))))
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from mamba import description, context, it, before
from expects import equal, have_len, be_true, be_false, expect, raise_error

from src.core.stories.nodes import AcceptanceCriteria, Epic, Story, StoryType, SubEpic
from src.core.stories.story_map import StoryMap
from src.formats.document.markdown.markdown_story_map import (
    MarkdownParseError,
    MarkdownStoryMap,
)


def _canonical_story_map_4_epics_3_sub_epics() -> StoryMap:
    story_map = StoryMap()
    for i in range(1, 5):
        epic = Epic(f"Epic {i}", i)
        story_map.epics.append(epic)
    first = story_map.epics[0]
    for j in range(1, 4):
        sub = SubEpic(f"SubEpic 1.{j}", j)
        story = Story(f"Story {j}", 1, StoryType.USER)
        story.acceptance_criteria.append(
            AcceptanceCriteria(name="AC 1", sequential_order=1, text=f"AC text {j}.1")
        )
        sub.stories.append(story)
        first.sub_epics.append(sub)
    return story_map


with description("a Markdown document") as self:
    with before.each:
        self.markdown = MarkdownStoryMap()

    with it("should contain no headings"):
        empty_story_map = StoryMap()
        text = self.markdown.render(empty_story_map)
        expect(text.count("#")).to(equal(0))

    with context(
        "that holds a rendered Story Map with 4 Epics and 3 SubEpics under the first Epic"
    ):
        with before.each:
            self.source = _canonical_story_map_4_epics_3_sub_epics()
            self.text = self.markdown.render(self.source)

        with it("should contain 4 top-level headings"):
            top_headings = [
                line for line in self.text.splitlines() if line.startswith("# ")
            ]
            expect(top_headings).to(have_len(4))

        with it("should contain 3 second-level headings under the first top-level heading"):
            lines = self.text.splitlines()
            # Slice lines between the first # heading and the next # heading
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

        with it("should list every Story as a bullet under its SubEpic"):
            lines = self.text.splitlines()
            story_bullets = [l for l in lines if l.startswith("- ")]
            expect(story_bullets).to(have_len(3))

        with it("should list every AcceptanceCriteria as an indented bullet under its Story"):
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
                self.source.remove_epic("Epic 1")
                self.new_text = self.markdown.render(self.source)

            with it("should contain 3 top-level headings"):
                top_headings = [
                    l for l in self.new_text.splitlines() if l.startswith("# ")
                ]
                expect(top_headings).to(have_len(3))

            with context("the headings for the removed Epic and its descendants"):
                with it("should be absent"):
                    expect("# Epic 1" in self.new_text).to(be_false)
                    expect("SubEpic 1.1" in self.new_text).to(be_false)

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
                    expect("## SubEpic 1.1" in self.new_text).to(be_true)
                    expect("## SubEpic 1.2" in self.new_text).to(be_true)
                    expect("## SubEpic 1.3" in self.new_text).to(be_true)

    with context("that is being read back into a MarkdownStoryMap"):
        with before.each:
            self.source = _canonical_story_map_4_epics_3_sub_epics()
            self.text = self.markdown.render(self.source)
            self.reconstructed = self.markdown.parse(self.text)

        with context("the reconstructed Story Map"):
            with it(
                "should hold every Epic, SubEpic, Story, and AcceptanceCriteria in sequential order"
            ):
                expect(self.reconstructed.epics).to(have_len(4))
                first_epic = self.reconstructed.epics[0]
                expect(first_epic.sub_epics).to(have_len(3))
                # One story per sub-epic, one AC per story in our fixture.
                expect(first_epic.sub_epics[0].stories).to(have_len(1))
                expect(first_epic.sub_epics[0].stories[0].acceptance_criteria).to(
                    have_len(1)
                )

    with context("that has been edited and synced back against a canonical Story Map"):
        with before.each:
            self.canonical = _canonical_story_map_4_epics_3_sub_epics()
            edited = _canonical_story_map_4_epics_3_sub_epics()
            edited.epics[0].name = "Epic 1 (edited)"
            edited.append_epic(Epic("Epic 5", 5))
            self.edited_text = self.markdown.render(edited)
            self.report = self.markdown.sync(self.edited_text, self.canonical)

        with context("the returned UpdateReport"):
            with it(
                "should list every add, remove, rename, reorder, and move applied to the document"
            ):
                expect(len(self.report.adds()) + len(self.report.renames()) >= 2).to(
                    be_true
                )

        with context("the reconstructed Story Map"):
            with it("should reflect every edit made to the document"):
                names = [e.name for e in self.canonical.epics]
                expect("Epic 1 (edited)" in names).to(be_true)
                expect("Epic 5" in names).to(be_true)

    with context("that includes metadata and prose around valid story structure"):
        with before.each:
            self.document = """# Story Map — Sample

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
            expect(self.reconstructed.epics[0].sub_epics).to(have_len(1))
            checkout = self.reconstructed.epics[0].sub_epics[0]
            expect(checkout.name).to(equal("Checkout"))
            expect(checkout.stories).to(have_len(1))
            expect(checkout.stories[0].acceptance_criteria).to(have_len(1))

    with context("that uses `(E)/(S)` outline notation"):
        with before.each:
            self.document = """# Story Map — pml-my

**Actors:** Customer, System

(E) Authenticate
    (E) Sign In
        (S) Self-Care Customer --> View Sign-In Form
        (S) Self-Care Customer --> Submit Sign-In Credentials

## Context Gaps
- prose bullets should be ignored in outline mode
"""
            self.reconstructed = self.markdown.parse(self.document)

        with it("should parse Epics, SubEpics, and Stories from outline lines"):
            expect(self.reconstructed.epics).to(have_len(1))
            expect(self.reconstructed.epics[0].name).to(equal("Authenticate"))
            expect(self.reconstructed.epics[0].sub_epics).to(have_len(1))
            sign_in = self.reconstructed.epics[0].sub_epics[0]
            expect(sign_in.name).to(equal("Sign In"))
            expect(sign_in.stories).to(have_len(2))
            expect(sign_in.stories[0].name).to(equal("View Sign-In Form"))
            expect(sign_in.stories[1].name).to(equal("Submit Sign-In Credentials"))

    with context("that uses heading-style stories and numbered acceptance criteria"):
        with before.each:
            self.document = """# Acceptance Criteria — Full Application

## Authenticate
### Sign In
#### Submit Sign-In Credentials
1. **WHEN** valid credentials are submitted
2. **WHEN** unverified email signs in
"""
            self.reconstructed = self.markdown.parse(self.document)

        with it("should parse deep headings as Story nodes and numbered lines as AcceptanceCriteria"):
            authenticate = self.reconstructed.epics[0]
            sign_in = authenticate.sub_epics[0]
            expect(sign_in.stories).to(have_len(1))
            story = sign_in.stories[0]
            expect(story.name).to(equal("Submit Sign-In Credentials"))
            expect(story.acceptance_criteria).to(have_len(2))

    with context("that is not a valid Markdown story map"):
        with context("the read"):
            with it("should be rejected"):
                bad_document = "this is not markdown\nno headings\njust prose"
                expect(lambda: self.markdown.parse(bad_document)).to(
                    raise_error(MarkdownParseError)
                )
