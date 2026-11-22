"""A number a Stories rule holds is written once, on the story map model: the check reads it there, and the rule's
text, the practice's guidance and the story map template are filled from it when the guidance is read. Exploratory
testing, shortcoming 8: the child-count band was typed in five places, and validate reported a band its rule did not
hold."""
import sys
from pathlib import Path
from unittest import mock

_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from expects import contain, equal, expect
from mamba import after, before, context, description, it

from cdd_guidance.practices.stories.model import story_map
from cdd_guidance.practices.stories.model.story_map import ChildBand, Epic, LayerBands, Story
from cdd_guidance.practices.stories.stories import Stories

_STORIES_FOLDER = Path(__file__).resolve().parents[1]
# Every way a band could be typed by hand in the practice's own text.
_TYPED_BANDS = ("3-9", "2-9", "4-9", "3 to 9", "2 to 9", "4 to 9")
_NARROWER = LayerBands(ChildBand("children", 3, 6), ChildBand("stories", 2, 5), ChildBand("stories", 4, 8))


def _sub_epic_of(stories: int) -> Epic:
    """A sub-epic holding that many stories, under an epic, with its map facts loaded."""
    epic, sub_epic = Epic("Manage Orders", 1), Epic("Place Order", 1)
    sub_epic.parent = epic
    epic.epics.append(sub_epic)
    for order in range(stories):
        story = Story(f"Submit Order {order + 1}", order + 1)
        story.parent = sub_epic
        sub_epic.stories.append(story)
    sub_epic.load_map_facts()
    return sub_epic


def _rule_text(slug: str) -> str:
    return next(rule.body for rule in Stories(fidelity="story_map").fidelities.current.every_rule if rule.slug == slug)


with description("the band of children a story map's layer holds") as self:
    with context("as the story map model holds it"):
        with it("should name a band for a node holding sub-epics, for a sub-epic and for a flat epic"):
            bands = story_map.LAYER_BANDS
            expect((bands.holding_sub_epics.written, bands.sub_epic.written, bands.flat_epic.written)).to(equal(("3-9", "2-9", "4-9")))

        with it("should give a sub-epic its target from the band, for the check to report"):
            expect(_sub_epic_of(10).child_target).to(equal(story_map.LAYER_BANDS.sub_epic.written))

    with context("in the practice's own files"):
        with it("should not be typed in the practice's document, which carries a marker for it"):
            written = (_STORIES_FOLDER / "stories.md").read_text(encoding="utf-8")
            expect([band for band in _TYPED_BANDS if band in written]).to(equal([]))

        with it("should not be typed in the story map template"):
            written = (_STORIES_FOLDER / "templates" / "md" / "story-map.md").read_text(encoding="utf-8")
            expect([band for band in _TYPED_BANDS if band in written]).to(equal([]))

        with it("should not be typed in the check, which reads the node's own target"):
            written = (_STORIES_FOLDER / "rules" / "story_map.py").read_text(encoding="utf-8")
            expect([band for band in _TYPED_BANDS if band in written]).to(equal([]))

    with context("as the guidance is read"):
        with it("should be written into the rule's text"):
            expect(_rule_text("child-count-fits-layer")).to(contain("groups 3-9 children", "holds 2-9", "holds 4-9"))

        with it("should be written into the practice's own guidance"):
            expect(Stories().section_text("guidance")).to(contain("groups 3-9 of them", "holds 2-9 stories", "holds 4-9"))

        with it("should be written into the story map template"):
            expect(str(Stories(fidelity="story_map").fidelities.current.templates)).to(contain("groups 3-9", "holds 2-9 stories", "holds 4-9"))

        with it("should leave no marker unfilled in the rule's text"):
            expect("{{" in _rule_text("child-count-fits-layer")).to(equal(False))

    with context("that is changed on the model, in that one place"):
        with before.each:
            self.changed = mock.patch.object(story_map, "LAYER_BANDS", _NARROWER)
            self.changed.start()

        with after.each:
            self.changed.stop()

        with it("should change the target the check reports"):
            expect((_sub_epic_of(6).child_band, _sub_epic_of(6).child_target)).to(equal(("error", "2-5")))

        with it("should change the rule's text"):
            expect(_rule_text("child-count-fits-layer")).to(contain("groups 3-6 children", "holds 2-5", "holds 4-8"))

        with it("should change the story map template"):
            expect(str(Stories(fidelity="story_map").fidelities.current.templates)).to(contain("holds 2-5 stories"))


with description("the most scenarios a story holds") as self:
    with it("should be held by the story map model"):
        expect(story_map.MOST_SCENARIOS).to(equal(7))

    with it("should be written into the rule's text from the model"):
        expect(_rule_text("story-scenarios-at-most-seven")).to(contain("at most 7 code scenarios", "More than 7"))

    with it("should not be typed in the rule's text in the practice's document"):
        written = (_STORIES_FOLDER / "stories.md").read_text(encoding="utf-8")
        expect(("at most 7" in written, "more than 7" in written.lower())).to(equal((False, False)))
