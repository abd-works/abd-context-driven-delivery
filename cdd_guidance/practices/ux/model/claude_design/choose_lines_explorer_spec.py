"""Mamba spec for the story explorer drawn from a real project's scenario files: pml-web's Choose Lines sub-epic, copied
into ``test-area/pml-web`` with its story map, domain model and UX map. The expected tree beside this spec is the Choose
Lines part of pml-web's published explorer (``ux/design-canvas/version-7``), each scenario file named from the
project's root, with the domain terms (``m``) and the Given and When realizations (``z``) each step group carries."""

import json
import tempfile
from pathlib import Path

from expects import equal, expect
from mamba import before, description, it

from cdd_guidance.practices.ux.model.claude_design.canvas_explorer import EXPLORER_FILE, CanvasExplorer
from cdd_guidance.practices.ux.model.claude_design.project_story_canvas import NoCanvasFixtures, ProjectStoryCanvas
from cdd_guidance.practices.ux.model.claude_design.story_canvas import ClaudeDesignStoryMap, StoryCanvasSetup
from cdd_guidance.practices.ux.model.json.nodes import JsonUxMap

_PROJECT = Path(__file__).resolve().parents[5] / "test-area" / "pml-web"
_EXPECTED = Path(__file__).with_name("choose_lines_explorer.expected.json")


def _named_from(node, root: str):
    """node with each file (``f``) it names written from root."""
    if isinstance(node, dict):
        return {key: value.removeprefix(root) if key == "f" else _named_from(value, root) for key, value in node.items()}
    if isinstance(node, list):
        return [_named_from(value, root) for value in node]
    return node


def _drawn_tree() -> list:
    """The explorer's tree as the story canvas draws it from the project's story map, scenario files and UX map."""
    canvas = ProjectStoryCanvas(_PROJECT, _PROJECT / "ux", _PROJECT / "tests", NoCanvasFixtures([]))
    story_map = canvas.story_map()
    ux_map = JsonUxMap().parse(json.loads((_PROJECT / "ux" / "ux.json").read_text(encoding="utf-8")))
    setup = StoryCanvasSetup(ux_map=ux_map, sources=canvas.sources(story_map), files_root=_PROJECT)
    page = json.loads(ClaudeDesignStoryMap(setup=setup).render(story_map))[f"project/{EXPLORER_FILE}"]
    with tempfile.TemporaryDirectory() as folder:
        written = Path(folder) / EXPLORER_FILE
        written.parent.mkdir(parents=True)
        written.write_text(page, encoding="utf-8")
        tree = CanvasExplorer(Path(folder)).tree()
    return _named_from(tree, _PROJECT.as_posix() + "/")


with description("the story explorer drawn from pml-web's Choose Lines scenario files") as self:
    with before.all:
        self.choose_lines = next(epic for epic in _drawn_tree() if epic["n"] == "Choose Lines")
        self.expected = json.loads(_EXPECTED.read_text(encoding="utf-8"))

    with it("should list the stories pml-web's explorer lists, in its order"):
        expect([story["n"] for story in self.choose_lines["s"]]).to(equal([story["n"] for story in self.expected["s"]]))

    with it("should group each scenario's steps as pml-web's explorer does, with its terms and realizations"):
        expect(self.choose_lines).to(equal(self.expected))
