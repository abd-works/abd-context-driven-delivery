"""Mamba spec: a story map written as a Stories sketch reads back as the same map."""

from expects import equal, expect
from mamba import before, description, it

from cdd_guidance.practices.stories.model.fixtures.round_trip_story_map import outline, round_trip_story_map
from cdd_guidance.practices.stories.model.sketch.sketch_story_model import SketchStoryModel


with description("a story map saved as a Stories sketch") as self:
    with before.each:
        self.story_map = round_trip_story_map()
        self.sketch = SketchStoryModel().render(self.story_map)
        self.read = SketchStoryModel().parse(self.sketch)

    with it("should write each story once"):
        expect(self.sketch.count("--> Submit Payment")).to(equal(1))

    with it("should read back every epic, story, kind, actor, background step, and scenario step"):
        expect(outline(self.read)).to(equal(outline(self.story_map)))
