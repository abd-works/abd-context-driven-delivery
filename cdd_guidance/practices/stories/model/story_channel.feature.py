"""Channel transform. Not collected with the other specs.

Loads the expected markdown, Draw.io, and TypeScript, writes each channel
under actual/from-{source}/to-{target}, and walks every node.

    .\\.venv\\Scripts\\python.exe -m mamba.cli practices/stories/model/story_channel.feature.py
"""

from pathlib import Path

from expects import equal, expect
from harness.annotations.name import Name
from cdd_guidance.practices.output_folder import OutputFolder
from mamba import describe, context, it, before, shared_context, included_context

from cdd_guidance.practices.stories.model.drawio.nodes import DrawIOStoryModel
from cdd_guidance.practices.stories.model.json.nodes import JsonStoryModel
from cdd_guidance.practices.stories.model.markdown.nodes import MarkdownScenario, MarkdownStoryModel
from cdd_guidance.practices.stories.model.miro.nodes import MiroStoryModel
from cdd_guidance.practices.stories.model.story_model import StoryModel
from cdd_guidance.practices.stories.stories import Stories
from cdd_guidance.practices.stories.model.java.java_story_model import JavaStoryModel
from cdd_guidance.practices.stories.model.javascript.javascript_story_model import JavaScriptStoryModel
from cdd_guidance.practices.stories.model.python.python_story_model import PythonStoryModel
from cdd_guidance.practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel
from cdd_guidance.practices.stories.model.code_story_model import CodeStoryNode

EXPECTED = Path(__file__).resolve().parent / "_examples" / "expected"
ACTUAL = Path(__file__).resolve().parent / "_examples" / "actual"

_DIAGRAM = ("drawio", "miro")
_CODE = ("typescript", "python", "javascript", "java")
_FLUENT = ("typescript", "javascript")


def _kebab(name: str) -> str:
    return Name(name).title_slug or "unnamed"


def walk(story_map: StoryModel) -> list:
    """Every epic, story, background, scenario, step, and, and increment, in map order."""
    entries = [entry for epic in story_map.epics for entry in _epic_entries(epic, 0)]
    for increment in story_map.increments:
        names = tuple(getattr(story, "name", story) for story in increment.stories)
        entries.append(("increment", increment.name, increment.sequential_order, names))
    return entries


def _epic_entries(epic, depth: int) -> list:
    entries = [("epic", depth, epic.name, epic.sequential_order, (epic.estimate or "").strip())]
    for story in epic.stories:
        entries.extend(_story_entries(story, depth + 1))
    for child in epic.epics:
        entries.extend(_epic_entries(child, depth + 1))
    return entries


def _story_entries(story, depth: int) -> list:
    story_type = getattr(story.story_type, "value", story.story_type)
    entries = [("story", depth, story.name, story.sequential_order, tuple(story.actors), story_type)]
    entries.extend(entry for background in story.backgrounds for entry in _background_entries(background, depth + 1))
    for scenario in story.scenarios:
        entries.append(("scenario", depth + 1, scenario.name, scenario.sequential_order))
        entries.extend(entry for background in scenario.backgrounds for entry in _background_entries(background, depth + 2))
        entries.extend(entry for step in scenario.steps for entry in _step_entries(step, depth + 2))
    return entries


def _background_entries(background, depth: int) -> list:
    return [("background", depth, background.name), *(entry for step in background.steps for entry in _step_entries(step, depth + 1))]


def _step_entries(step, depth: int) -> list:
    return [("step", depth, step.keyword, step.text), *(("and", depth + 1, extra.keyword, extra.text) for extra in step.ands)]


def kept(entries: list, channel: str) -> list:
    """The nodes this channel writes into its files."""
    if channel in _DIAGRAM:
        return [entry for entry in entries if entry[0] in ("epic", "story", "increment")]
    if channel in _CODE:
        return _stored_code(_code_entries(entries))
    return entries


def _code_entries(entries: list) -> list:
    """Code folders store a slug. Scenario and step text stay as written."""
    selected = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        if entry[0] != "story":
            if entry[0] == "epic":
                selected.append(("epic", entry[1], _kebab(entry[2]), entry[3], entry[4]))
            index += 1
            continue
        block = [entry]
        index += 1
        while index < len(entries) and entries[index][0] not in ("story", "epic"):
            block.append(entries[index])
            index += 1
        story = block[0]
        selected.append(("story", story[1], _kebab(story[2]), story[3], tuple(story[4]), story[5]))
        step_depth = story[1] + 2
        for item in block[1:]:
            if item[0] == "background":
                continue
            if item[0] in ("step", "and") and item[1] > step_depth:
                item = (item[0], item[1] - 1, *item[2:])
            selected.append(item)
    return selected




def _grouped(entries: list) -> list:
    """Sort each epic's children by name. Code files are read in path order."""
    def take(items: list, depth: int) -> list:
        blocks = []
        index = 0
        while index < len(items):
            entry = items[index]
            if entry[0] == "epic" and entry[1] == depth:
                end = index + 1
                while end < len(items) and not (items[end][0] == "epic" and items[end][1] <= depth):
                    end += 1
                blocks.append((entry[2], [entry, *take(items[index + 1:end], depth + 1)]))
                index = end
                continue
            if entry[0] == "story" and entry[1] == depth:
                end = index + 1
                while end < len(items) and items[end][0] not in ("story", "epic"):
                    end += 1
                blocks.append((entry[2], items[index:end]))
                index = end
                continue
            blocks.append(("", [entry]))
            index += 1
        ordered = []
        for _name, block in sorted(blocks, key=lambda item: item[0]):
            ordered.extend(block)
        return ordered

    return take(entries, 0)


def _normalize_loaded(entries: list, channel: str) -> list:
    if channel not in _CODE:
        return entries
    normalized = []
    for entry in entries:
        if entry[0] == "epic":
            normalized.append(("epic", entry[1], _kebab(entry[2]), entry[3], entry[4]))
        elif entry[0] == "story":
            normalized.append(("story", entry[1], _kebab(entry[2]), entry[3], tuple(entry[4]), entry[5]))
        elif entry[0] == "background":
            continue
        elif entry[0] in ("step", "and"):
            normalized.append(entry)
        else:
            normalized.append(entry)
    return _stored_code(normalized)


def _stored_code(entries: list) -> list:
    """Code files keep names, actors, and steps. Folder order replaces sequential order."""
    stored = []
    for entry in entries:
        if entry[0] in ("epic", "story", "scenario"):
            stored.append((*entry[:3], 0, *entry[4:]))
        else:
            stored.append(entry)
    return _grouped(stored)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _write_tree(folder: Path, files: dict) -> None:
    for relative, body in files.items():
        _write(folder / relative, body)


def _read_tree(folder: Path) -> dict:
    files = {}
    for path in folder.rglob("*"):
        if path.is_file():
            files[path.relative_to(folder).as_posix()] = path.read_text(encoding="utf-8")
    return files


def _write_markdown(source: StoryModel, folder: Path) -> None:
    _write(folder / "story-map.md", MarkdownStoryModel(source).save())

    def visit(epic, parts: list) -> None:
        for story in epic.stories:
            if not story.scenarios:
                continue
            _write(
                folder.joinpath(*parts, f"{_kebab(story.name)}_story.spec.md"),
                MarkdownScenario.render_scenarios(
                    story.scenarios,
                    story_name=story.name,
                    story_backgrounds=story.backgrounds,
                ),
            )
        for child in epic.epics:
            visit(child, parts + [_kebab(child.name)])

    for epic in source.epics:
        visit(epic, [_kebab(epic.name)])


_SOURCES = ("markdown", "drawio", "typescript")
_CHANNELS = ("markdown", "json", "drawio", "miro", "typescript", "python", "javascript", "java")


def _expected_typescript() -> dict:
    files = {}
    for path in EXPECTED.rglob("*_story.spec.ts"):
        relative = path.relative_to(EXPECTED).as_posix()
        key = "tests/" + relative[: -len("_story.spec.ts")] + "_story.test.ts"
        files[key] = path.read_text(encoding="utf-8")
    return files


def load_source(name: str) -> StoryModel:
    if name == "markdown":
        return Stories().read_folder(EXPECTED)
    if name == "drawio":
        return DrawIOStoryModel().load((EXPECTED / "story-map.drawio").read_text(encoding="utf-8"))
    return TypeScriptStoryModel().load(_expected_typescript())


_CODE_MAPS = {
    "typescript": TypeScriptStoryModel,
    "python": PythonStoryModel,
    "javascript": JavaScriptStoryModel,
    "java": JavaStoryModel,
}


def save_channel(source_name: str, target: str, source: StoryModel) -> StoryModel:
    """Write source through the target channel, then read the written files back."""
    folder = ACTUAL / f"from-{source_name}" / f"to-{target}"
    OutputFolder(folder).clear()
    folder.mkdir(parents=True)
    _write_channel(folder, target, source)
    return _read_channel(folder, target)


def _write_channel(folder: Path, target: str, source: StoryModel) -> None:
    if target == "markdown":
        _write_markdown(source, folder)
    elif target == "json":
        _write(folder / "story-graph.json", JsonStoryModel().render(JsonStoryModel(source)))
    elif target == "drawio":
        _write(folder / "story-map.drawio", DrawIOStoryModel(source).save())
    elif target == "miro":
        _write(folder / "story-map.svg", MiroStoryModel(source).save())
    else:
        _write_tree(folder, _CODE_MAPS[target](source).save())


def _read_channel(folder: Path, target: str) -> StoryModel:
    if target == "markdown":
        return MarkdownStoryModel.from_workspace(folder)
    if target == "json":
        return JsonStoryModel().parse((folder / "story-graph.json").read_text(encoding="utf-8"))
    if target == "drawio":
        return DrawIOStoryModel().load((folder / "story-map.drawio").read_text(encoding="utf-8"))
    if target == "miro":
        return MiroStoryModel().load((folder / "story-map.svg").read_text(encoding="utf-8"))
    return _CODE_MAPS[target]().load(_read_tree(folder))


def _story_names(entries: list) -> list:
    return [entry[2] for entry in entries if entry[0] == "story"]


def _as_loaded(example, entries):
    if example.channel in _CODE:
        return _normalize_loaded(entries, example.channel)
    return entries


_STORY_WITHOUT_SCENARIOS = "Hand Off Sign Up To Onboarding"


with shared_context("a story map saved through a channel"):
    with it("should match each epic, sub-epic, story, actor, background, scenario, example, and step"):
        expected = self.source
        actual = self.loaded
        stores_scenarios = self.channel not in ("drawio", "miro")
        stores_steps = stores_scenarios

        def node_name(name):
            if self.channel in _CODE:
                return _kebab(name)
            return name

        def clauses(steps):
            """(keyword, text, [(keyword, text)]) per clause. The fluent brace surface chains a step that
            repeats the previous step's phase as .and(), so for those channels it reads back as an And."""
            entries = []
            for step in steps:
                ands = [(extra.keyword, extra.text) for extra in step.ands]
                if self.channel in _FLUENT and entries and step.step_type == entries[-1][3]:
                    entries[-1][2].extend([("And", step.text)] + ands)
                    continue
                entries.append((step.keyword, step.text, ands, step.step_type))
            return [entry[:3] for entry in entries]

        def check_steps(actual_steps, expected_steps):
            expect(clauses(actual_steps)).to(equal(clauses(expected_steps)))

        def check_examples(actual_examples, expected_examples):
            expect(sorted(actual_examples)).to(equal(sorted(expected_examples)))
            for example_name, expected_example in expected_examples.items():
                expect(actual_examples[example_name].cells()).to(equal(expected_example.cells()))

        def check_backgrounds(actual_backgrounds, expected_backgrounds):
            expect(len(actual_backgrounds)).to(equal(len(expected_backgrounds)))
            for background_index, expected_background in enumerate(expected_backgrounds):
                actual_background = actual_backgrounds[background_index]
                expect(actual_background.name).to(equal(expected_background.name))
                if stores_steps:
                    check_steps(actual_background.steps, expected_background.steps)
                if stores_scenarios:
                    check_examples(actual_background.examples, expected_background.examples)

        def check_epics(actual_epics, expected_epics):
            expect(len(actual_epics)).to(equal(len(expected_epics)))
            for epic_index, expected_epic in enumerate(expected_epics):
                actual_epic = actual_epics[epic_index]
                expect(node_name(actual_epic.name)).to(equal(node_name(expected_epic.name)))
                expected_stories = expected_epic.stories
                expect(len(actual_epic.stories)).to(equal(len(expected_stories)))
                for story_index, expected_story in enumerate(expected_stories):
                    actual_story = actual_epic.stories[story_index]
                    expect(node_name(actual_story.name)).to(equal(node_name(expected_story.name)))
                    expect(tuple(actual_story.actors)).to(equal(tuple(expected_story.actors)))
                    if not stores_scenarios:
                        continue
                    check_backgrounds(actual_story.backgrounds, expected_story.backgrounds)
                    expect(len(actual_story.scenarios)).to(equal(len(expected_story.scenarios)))
                    for scenario_index, expected_scenario in enumerate(expected_story.scenarios):
                        actual_scenario = actual_story.scenarios[scenario_index]
                        expect(actual_scenario.name).to(equal(expected_scenario.name))
                        check_backgrounds(actual_scenario.backgrounds, expected_scenario.backgrounds)
                        check_examples(actual_scenario.examples, expected_scenario.examples)
                        if stores_steps:
                            check_steps(actual_scenario.steps, expected_scenario.steps)
                check_epics(actual_epic.epics, expected_epic.epics)

        check_epics(actual.epics, expected.epics)


def _open(example, source_name: str, target: str) -> None:
    example.source = example.sources[source_name]
    example.source_walk = example.walks[source_name]
    example.channel = target
    example.loaded = save_channel(source_name, target, example.source)


with describe("a story map"):
    with before.all:
        OutputFolder(ACTUAL).clear()
        self.sources = {name: load_source(name) for name in _SOURCES}
        self.walks = {name: walk(story_map) for name, story_map in self.sources.items()}

    with context("that is loaded from the expected markdown"):
        with it("should include every epic, story, scenario, and step"):
            kinds = {entry[0] for entry in self.walks["markdown"]}
            expect(kinds.issuperset({"epic", "story", "scenario", "step"})).to(equal(True))

    with describe("from markdown"):
        with describe("to markdown"):
            with before.all:
                _open(self, "markdown", "markdown")
            with included_context("a story map saved through a channel"):
                pass
            with context("that is saved a second time"):
                with it("should keep the same nodes"):
                    again = save_channel("markdown", "markdown", self.loaded)
                    expect(walk(again)).to(equal(walk(self.loaded)))
        with describe("to json"):
            with before.all:
                _open(self, "markdown", "json")
            with included_context("a story map saved through a channel"):
                pass
            with it("should bring the scenarios back with their steps"):
                kinds = {entry[0] for entry in walk(self.loaded)}
                expect(kinds.issuperset({"scenario", "step"})).to(equal(True))
        with describe("to drawio"):
            with before.all:
                _open(self, "markdown", "drawio")
            with included_context("a story map saved through a channel"):
                pass
            with context("with scenarios left out of the file"):
                with it("should bring the epics and stories back and leave the scenarios out"):
                    kinds = {entry[0] for entry in walk(self.loaded)}
                    expect("story" in kinds and "scenario" not in kinds).to(equal(True))
        with describe("to miro"):
            with before.all:
                _open(self, "markdown", "miro")
            with included_context("a story map saved through a channel"):
                pass
            with context("with scenarios left out of the file"):
                with it("should bring the epics and stories back and leave the scenarios out"):
                    kinds = {entry[0] for entry in walk(self.loaded)}
                    expect("story" in kinds and "scenario" not in kinds).to(equal(True))
        with describe("to typescript"):
            with before.all:
                _open(self, "markdown", "typescript")
            with included_context("a story map saved through a channel"):
                pass
            with context("with a story that has no scenarios"):
                with it("should bring that story back"):
                    names = _story_names(_as_loaded(self, walk(self.loaded)))
                    expect(_kebab(_STORY_WITHOUT_SCENARIOS) in names).to(equal(True))
        with describe("to python"):
            with before.all:
                _open(self, "markdown", "python")
            with included_context("a story map saved through a channel"):
                pass
            with context("with a story that has no scenarios"):
                with it("should bring that story back"):
                    names = _story_names(_as_loaded(self, walk(self.loaded)))
                    expect(_kebab(_STORY_WITHOUT_SCENARIOS) in names).to(equal(True))
        with describe("to javascript"):
            with before.all:
                _open(self, "markdown", "javascript")
            with included_context("a story map saved through a channel"):
                pass
            with context("with a story that has no scenarios"):
                with it("should bring that story back"):
                    names = _story_names(_as_loaded(self, walk(self.loaded)))
                    expect(_kebab(_STORY_WITHOUT_SCENARIOS) in names).to(equal(True))
        with describe("to java"):
            with before.all:
                _open(self, "markdown", "java")
            with included_context("a story map saved through a channel"):
                pass
            with context("with a story that has no scenarios"):
                with it("should bring that story back"):
                    names = _story_names(_as_loaded(self, walk(self.loaded)))
                    expect(_kebab(_STORY_WITHOUT_SCENARIOS) in names).to(equal(True))

    with describe("from drawio"):
        with describe("to markdown"):
            with before.all:
                _open(self, "drawio", "markdown")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to json"):
            with before.all:
                _open(self, "drawio", "json")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to drawio"):
            with before.all:
                _open(self, "drawio", "drawio")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to miro"):
            with before.all:
                _open(self, "drawio", "miro")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to typescript"):
            with before.all:
                _open(self, "drawio", "typescript")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to python"):
            with before.all:
                _open(self, "drawio", "python")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to javascript"):
            with before.all:
                _open(self, "drawio", "javascript")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to java"):
            with before.all:
                _open(self, "drawio", "java")
            with included_context("a story map saved through a channel"):
                pass

    with describe("from typescript"):
        with describe("to markdown"):
            with before.all:
                _open(self, "typescript", "markdown")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to json"):
            with before.all:
                _open(self, "typescript", "json")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to drawio"):
            with before.all:
                _open(self, "typescript", "drawio")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to miro"):
            with before.all:
                _open(self, "typescript", "miro")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to typescript"):
            with before.all:
                _open(self, "typescript", "typescript")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to python"):
            with before.all:
                _open(self, "typescript", "python")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to javascript"):
            with before.all:
                _open(self, "typescript", "javascript")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to java"):
            with before.all:
                _open(self, "typescript", "java")
            with included_context("a story map saved through a channel"):
                pass
