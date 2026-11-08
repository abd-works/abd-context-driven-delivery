"""Spec support: run Stories graph rules on example sources the way validate runs them.

An example's story file is written onto a graph of its own through the story model, as a live load writes a story map,
so every node carries the type and facts a live build gives it. Each rule then runs through the practice's schema, so a
rule the schema never applies to a node type finds nothing there and its example fails.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

from harness.graph.graph import Graph
from harness.graph.rule_context import RuleCheckContext
from harness.graph.rule_fixture import RulePair, SchemaRuleRun

from cdd_guidance.practices.stories.model.source_location import SourceLocation
from cdd_guidance.practices.stories.model.story_model import Epic, Example, Scenario, Step, StepType, Story, StoryModel
from cdd_guidance.practices.stories.rules import BY_SLUG
from cdd_guidance.practices.stories.stories import Stories

_EXAMPLES = Path(__file__).resolve().parents[1] / "model" / "typescript" / "_examples"
_STORY_CALL = re.compile(r"""story\s*\(\s*['"]([^'"]+)['"]""")
_GIVEN_CALL = re.compile(r"""given\s*\(\s*['"]([^'"]+)['"]""")
# The story a story file that names none holds.
_FIXTURE_STORY = "Submit Fixture Story"


def stories_rule_by_slug(slug: str):
    return BY_SLUG[slug]


class StoryFixture:
    """Example files in a folder of their own, with the story file among them written onto a graph through the story
    model: an epic holding a story for each ``story(...)`` call the file makes (one story when it makes none), whose
    scenario holds a Given for each ``given(...)`` call and each example named. The fixture keeps the folder, which goes
    when the fixture does."""

    def __init__(self, files: dict[str, str], story_file: str, examples: tuple[str, ...] = ()) -> None:
        self._folder = tempfile.TemporaryDirectory()
        self.root = Path(self._folder.name)
        for relative, text in files.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        graph = Graph()
        graph.open(self.root)
        self.practice = graph.practice_of(Stories)
        self._story_map(files[story_file], story_file, examples).record(self.practice)

    @classmethod
    def from_folder(cls, folder: Path, story_file: str, examples: tuple[str, ...] = ()) -> StoryFixture:
        """The files under folder, named from it."""
        files = {path.relative_to(folder).as_posix(): path.read_text(encoding="utf-8") for path in folder.rglob("*") if path.is_file()}
        return cls(files, story_file, examples)

    def hits(self, rule) -> list[str]:
        """Each message the rule reports where validate keeps it."""
        return SchemaRuleRun(rule, RuleCheckContext(self.practice, self.root)).hits()

    def _story_map(self, text: str, story_file: str, examples: tuple[str, ...]) -> StoryModel:
        epic = Epic("Submit Fixture Stories", 1)
        stories = [Story(name, order) for order, name in enumerate(_STORY_CALL.findall(text) or [_FIXTURE_STORY], start=1)]
        for story in stories:
            story.source = SourceLocation(story_file, 1, 1)
            epic.append_story(story)
        scenario = Scenario("Submit the fixture", 1)
        scenario.steps = [Step(given, StepType.GIVEN, order, keyword="Given") for order, given in enumerate(_GIVEN_CALL.findall(text), start=1)]
        for name in examples:
            scenario.examples[name] = Example(name)
        stories[0].scenarios = [scenario]
        story_map = StoryModel()
        story_map.append_epic(epic)
        story_map.source_texts[story_file] = text
        return story_map


def assert_stories_ts_pair(slug: str, fault_source: str, clean_source: str, *, relative: str = "faultyAsset.ts", clean_relative: str | None = None) -> None:
    """The rule flags the story file fault_source and passes clean_source."""
    clean_relative = clean_relative or relative
    faulty = StoryFixture({relative: fault_source.strip() + "\n"}, relative)
    repaired = StoryFixture({clean_relative: clean_source.strip() + "\n"}, clean_relative)
    RulePair(stories_rule_by_slug(slug), faulty, repaired).check()


def assert_stories_example_pair(slug: str) -> None:
    """The rule flags its example's faulty asset and passes its repaired one."""
    root = _EXAMPLES / slug
    assert_stories_ts_pair(
        slug,
        (root / "faulty" / "faultyAsset.ts").read_text(encoding="utf-8"),
        (root / "repaired" / "repairedAsset.ts").read_text(encoding="utf-8"),
        relative="faultyAsset.ts",
        clean_relative="repairedAsset.ts",
    )


def assert_stories_folder_pair(slug: str, story_file: str, examples: tuple[str, ...]) -> None:
    """The rule flags its example's faulty folder and passes its repaired one, each read with story_file as the story
    file whose scenario uses examples."""
    root = _EXAMPLES / slug
    faulty = StoryFixture.from_folder(root / "faulty", story_file, examples)
    repaired = StoryFixture.from_folder(root / "repaired", story_file, examples)
    RulePair(stories_rule_by_slug(slug), faulty, repaired).check()
