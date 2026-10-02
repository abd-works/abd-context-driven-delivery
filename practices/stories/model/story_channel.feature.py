"""Channel transform. Not collected with the other specs.

Loads the expected markdown, Draw.io, and TypeScript, writes each channel
under actual/from-{source}/to-{target}, and walks every node.

    .\\.venv\\Scripts\\python.exe -m mamba.cli practices/stories/model/story_channel.feature.py
"""

import shutil
from pathlib import Path

from expects import equal, expect
from mamba import describe, context, it, before, shared_context, included_context

from practices.stories.model.drawio.nodes import DrawIOStoryModel
from practices.stories.model.json.nodes import JsonStoryModel
from practices.stories.model.markdown.nodes import MarkdownScenario, MarkdownStoryModel
from practices.stories.model.miro.nodes import MiroStoryModel
from practices.stories.model.story_model import StoryModel, StoryModelFactory
from practices.stories.model.java.java_story_model import JavaStoryModel
from practices.stories.model.javascript.javascript_story_model import JavaScriptStoryModel
from practices.stories.model.python.python_story_model import PythonStoryModel
from practices.stories.model.codeql.codeql_model import StoryModel as CodeQLStoryModel
from practices.stories.model.typescript.typescript_story_model import TypeScriptStoryModel
from practices.stories.model.code_story_model import CodeStoryNode
from practices.stories.model.knowledge_graph.nodes import KnowledgeGraphStoryModel

EXPECTED = Path(__file__).resolve().parent / ".examples" / "expected"
ACTUAL = Path(__file__).resolve().parent / ".examples" / "actual"

_DIAGRAM = ("drawio", "miro")
_CODE_WITH_EMPTY_STORIES = ("typescript",)
_CODE = ("typescript", "python", "javascript", "java")


def _kebab(name: str) -> str:
    import re
    return re.sub(r"[^0-9a-z]+", "-", name.strip().lower()).strip("-") or "unnamed"


def walk(story_map: StoryModel) -> list:
    """Every epic, story, background, scenario, step, and, and increment, in map order."""
    rows = []

    def visit_step(step, depth: int) -> None:
        rows.append(("step", depth, step.keyword, step.text))
        for extra in step.ands:
            rows.append(("and", depth + 1, extra.keyword, extra.text))

    def visit_epic(epic, depth: int) -> None:
        rows.append(("epic", depth, epic.name, epic.sequential_order, (epic.estimate or "").strip()))
        for story in epic.stories:
            story_type = getattr(story.story_type, "value", story.story_type)
            rows.append((
                "story",
                depth + 1,
                story.name,
                story.sequential_order,
                tuple(story.actors),
                story_type,
            ))
            for background in story.backgrounds:
                rows.append(("background", depth + 2, background.name))
                for step in background.steps:
                    visit_step(step, depth + 3)
            for scenario in story.scenarios:
                rows.append(("scenario", depth + 2, scenario.name, scenario.sequential_order))
                for background in scenario.backgrounds:
                    rows.append(("background", depth + 3, background.name))
                    for step in background.steps:
                        visit_step(step, depth + 4)
                for step in scenario.steps:
                    visit_step(step, depth + 3)
        for child in epic.epics:
            visit_epic(child, depth + 1)

    for epic in story_map.epics:
        visit_epic(epic, 0)
    for increment in story_map.increments:
        names = tuple(getattr(story, "name", story) for story in increment.stories)
        rows.append(("increment", increment.name, increment.sequential_order, names))
    return rows


def kept(rows: list, channel: str) -> list:
    """The nodes this channel writes into its files."""
    if channel in _DIAGRAM:
        return [row for row in rows if row[0] in ("epic", "story", "increment")]
    if channel == "json":
        return [row for row in rows if row[0] not in ("step", "and", "background")]
    if channel in _CODE and channel not in _CODE_WITH_EMPTY_STORIES:
        return _stored_code(_code_rows(rows, require_scenarios=True))
    if channel in _CODE:
        return _stored_code(_code_rows(rows, require_scenarios=False))
    return rows


def _code_rows(rows: list, *, require_scenarios: bool) -> list:
    """Code folders store a slug. Scenario and step text stay as written."""
    selected = []
    index = 0
    while index < len(rows):
        row = rows[index]
        if row[0] != "story":
            if row[0] == "epic":
                selected.append(("epic", row[1], _kebab(row[2]), row[3], row[4]))
            index += 1
            continue
        block = [row]
        index += 1
        while index < len(rows) and rows[index][0] not in ("story", "epic"):
            block.append(rows[index])
            index += 1
        has_scenario = any(item[0] == "scenario" for item in block)
        if require_scenarios and not has_scenario:
            continue
        story = block[0]
        selected.append(("story", story[1], _kebab(story[2]), story[3], tuple(story[4]), story[5]))
        step_depth = story[1] + 2
        for item in block[1:]:
            if item[0] == "background":
                continue
            if item[0] in ("step", "and") and item[1] > step_depth:
                item = (item[0], item[1] - 1, *item[2:])
            selected.append(item)
    return _drop_empty_epics(selected) if require_scenarios else selected


def _drop_empty_epics(rows: list) -> list:
    kept_rows = []
    index = 0
    while index < len(rows):
        row = rows[index]
        if row[0] != "epic":
            kept_rows.append(row)
            index += 1
            continue
        depth = row[1]
        end = index + 1
        while end < len(rows) and not (rows[end][0] == "epic" and rows[end][1] <= depth):
            end += 1
        body = _drop_empty_epics(rows[index + 1:end])
        if body:
            kept_rows.append(row)
            kept_rows.extend(body)
        index = end
    return kept_rows


def _grouped(rows: list) -> list:
    """Sort each epic's children by name. Code files are read in path order."""
    def take(items: list, depth: int) -> list:
        blocks = []
        index = 0
        while index < len(items):
            row = items[index]
            if row[0] == "epic" and row[1] == depth:
                end = index + 1
                while end < len(items) and not (items[end][0] == "epic" and items[end][1] <= depth):
                    end += 1
                blocks.append((row[2], [row, *take(items[index + 1:end], depth + 1)]))
                index = end
                continue
            if row[0] == "story" and row[1] == depth:
                end = index + 1
                while end < len(items) and items[end][0] not in ("story", "epic"):
                    end += 1
                blocks.append((row[2], items[index:end]))
                index = end
                continue
            blocks.append(("", [row]))
            index += 1
        ordered = []
        for _name, block in sorted(blocks, key=lambda item: item[0]):
            ordered.extend(block)
        return ordered

    return take(rows, 0)


def _normalize_loaded(rows: list, channel: str) -> list:
    if channel not in _CODE:
        return rows
    normalized = []
    for row in rows:
        if row[0] == "epic":
            normalized.append(("epic", row[1], _kebab(row[2]), row[3], row[4]))
        elif row[0] == "story":
            normalized.append(("story", row[1], _kebab(row[2]), row[3], tuple(row[4]), row[5]))
        elif row[0] == "background":
            continue
        elif row[0] in ("step", "and"):
            normalized.append(row)
        else:
            normalized.append(row)
    if channel not in _CODE_WITH_EMPTY_STORIES:
        normalized = _drop_empty_epics(normalized)
    return _stored_code(normalized)


def _stored_code(rows: list) -> list:
    """Code files keep names, actors, and steps. Folder order replaces sequential order."""
    stored = []
    for row in rows:
        if row[0] in ("epic", "story", "scenario"):
            stored.append((*row[:3], 0, *row[4:]))
        else:
            stored.append(row)
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
        return StoryModelFactory.load(str(EXPECTED))
    if name == "drawio":
        return DrawIOStoryModel().load((EXPECTED / "story-map.drawio").read_text(encoding="utf-8"))
    return TypeScriptStoryModel().load(_expected_typescript())


def save_channel(source_name: str, target: str, source: StoryModel) -> StoryModel:
    folder = ACTUAL / f"from-{source_name}" / f"to-{target}"
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)
    if target == "markdown":
        _write_markdown(source, folder)
        return MarkdownStoryModel.from_workspace(folder)
    if target == "json":
        copied = JsonStoryModel(source)
        _write(folder / "story-graph.json", JsonStoryModel().render(copied))
        return JsonStoryModel().parse((folder / "story-graph.json").read_text(encoding="utf-8"))
    if target == "drawio":
        _write(folder / "story-map.drawio", DrawIOStoryModel(source).save())
        return DrawIOStoryModel().load((folder / "story-map.drawio").read_text(encoding="utf-8"))
    if target == "miro":
        _write(folder / "story-map.svg", MiroStoryModel(source).save())
        return MiroStoryModel().load((folder / "story-map.svg").read_text(encoding="utf-8"))
    if target == "codeql":
        _write_tree(folder, TypeScriptStoryModel(source).save())
        return CodeQLStoryModel.load_content(folder)
    if target == "knowledge_graph":
        copied = KnowledgeGraphStoryModel(source)
        _write(folder / "story-map.kg", copied.save())
        return copied
    maps = {
        "typescript": TypeScriptStoryModel,
        "python": PythonStoryModel,
        "javascript": JavaScriptStoryModel,
        "java": JavaStoryModel,
    }
    story_map_type = maps[target]
    _write_tree(folder, story_map_type(source).save())
    return story_map_type().load(_read_tree(folder))


def _story_names(rows: list) -> list:
    return [row[2] for row in rows if row[0] == "story"]


def _as_loaded(example, rows):
    if example.channel in _CODE:
        return _normalize_loaded(rows, example.channel)
    return rows


_STORY_WITHOUT_SCENARIOS = "Hand Off Sign Up To Onboarding"


with shared_context("a story map saved through a channel"):
    with it("should match each epic, sub-epic, story, actor, background, scenario, example, and step"):
        expected = self.source
        actual = self.loaded
        stores_scenarios = self.channel not in ("drawio", "miro")
        stores_steps = self.channel not in ("drawio", "miro", "json")
        drops_empty_stories = self.channel in ("python", "javascript", "java")

        def node_name(name):
            if self.channel in _CODE:
                return _kebab(name)
            return name

        def kept_stories(epic):
            stories = list(epic.stories)
            if drops_empty_stories:
                stories = [story for story in stories if story.scenarios]
            return stories

        def kept_epics(epics):
            kept = []
            for epic in epics:
                if drops_empty_stories and not kept_stories(epic) and not kept_epics(epic.epics):
                    continue
                kept.append(epic)
            return kept

        def check_steps(actual_steps, expected_steps):
            expect(len(actual_steps)).to(equal(len(expected_steps)))
            for step_index, expected_step in enumerate(expected_steps):
                actual_step = actual_steps[step_index]
                expect(actual_step.keyword).to(equal(expected_step.keyword))
                expect(actual_step.text).to(equal(expected_step.text))
                expect(len(actual_step.ands)).to(equal(len(expected_step.ands)))
                for and_index, expected_and in enumerate(expected_step.ands):
                    actual_and = actual_step.ands[and_index]
                    expect(actual_and.keyword).to(equal(expected_and.keyword))
                    expect(actual_and.text).to(equal(expected_and.text))

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
            expected_epics = kept_epics(expected_epics)
            expect(len(actual_epics)).to(equal(len(expected_epics)))
            for epic_index, expected_epic in enumerate(expected_epics):
                actual_epic = actual_epics[epic_index]
                expect(node_name(actual_epic.name)).to(equal(node_name(expected_epic.name)))
                expected_stories = kept_stories(expected_epic)
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
        if self.channel == "codeql":
            from practices.clean_engineering.model.codeql.codeql_model import OoadClass

            if self.loaded.graph.nodes_of_type(OoadClass):
                _expect_clean_engineering_relationships(self.loaded)


def _open_codeql(example, source_name: str) -> None:
    _open(example, source_name, "codeql")
    folder = ACTUAL / f"from-{source_name}" / "to-codeql"
    example.source = TypeScriptStoryModel().load(_read_tree(folder))


def _open(example, source_name: str, target: str) -> None:
    example.source = example.sources[source_name]
    example.source_walk = example.walks[source_name]
    example.channel = target
    example.loaded = save_channel(source_name, target, example.source)


with describe("a story map"):
    with before.all:
        if ACTUAL.exists():
            shutil.rmtree(ACTUAL)
        self.sources = {name: load_source(name) for name in _SOURCES}
        self.walks = {name: walk(story_map) for name, story_map in self.sources.items()}

    with context("that is loaded from the expected markdown"):
        with it("should include every epic, story, scenario, and step"):
            kinds = {row[0] for row in self.walks["markdown"]}
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
            with context("with steps left out of the file"):
                with it("should bring the scenarios back and leave the steps out"):
                    kinds = {row[0] for row in walk(self.loaded)}
                    expect("scenario" in kinds and "step" not in kinds).to(equal(True))
        with describe("to drawio"):
            with before.all:
                _open(self, "markdown", "drawio")
            with included_context("a story map saved through a channel"):
                pass
            with context("with scenarios left out of the file"):
                with it("should bring the epics and stories back and leave the scenarios out"):
                    kinds = {row[0] for row in walk(self.loaded)}
                    expect("story" in kinds and "scenario" not in kinds).to(equal(True))
        with describe("to miro"):
            with before.all:
                _open(self, "markdown", "miro")
            with included_context("a story map saved through a channel"):
                pass
            with context("with scenarios left out of the file"):
                with it("should bring the epics and stories back and leave the scenarios out"):
                    kinds = {row[0] for row in walk(self.loaded)}
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
                with it("should leave that story out"):
                    names = _story_names(_as_loaded(self, walk(self.loaded)))
                    expect(_kebab(_STORY_WITHOUT_SCENARIOS) in names).to(equal(False))
        with describe("to javascript"):
            with before.all:
                _open(self, "markdown", "javascript")
            with included_context("a story map saved through a channel"):
                pass
            with context("with a story that has no scenarios"):
                with it("should leave that story out"):
                    names = _story_names(_as_loaded(self, walk(self.loaded)))
                    expect(_kebab(_STORY_WITHOUT_SCENARIOS) in names).to(equal(False))
        with describe("to java"):
            with before.all:
                _open(self, "markdown", "java")
            with included_context("a story map saved through a channel"):
                pass
            with context("with a story that has no scenarios"):
                with it("should leave that story out"):
                    names = _story_names(_as_loaded(self, walk(self.loaded)))
                    expect(_kebab(_STORY_WITHOUT_SCENARIOS) in names).to(equal(False))
        with describe("to codeql"):
            with before.all:
                _open_codeql(self, "markdown")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to knowledge graph"):
            with before.all:
                _open(self, "markdown", "knowledge_graph")
            with included_context("a story map saved through a channel"):
                pass

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
        with describe("to codeql"):
            with before.all:
                _open_codeql(self, "drawio")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to knowledge graph"):
            with before.all:
                _open(self, "drawio", "knowledge_graph")
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
        with describe("to codeql"):
            with before.all:
                _open_codeql(self, "typescript")
            with included_context("a story map saved through a channel"):
                pass
        with describe("to knowledge graph"):
            with before.all:
                _open(self, "typescript", "knowledge_graph")
            with included_context("a story map saved through a channel"):
                pass

with describe("a story model populated from the stored codeql database"):
    with it("should write the typescript stories and keep the clean engineering associations"):
        from harness.knowledge_graph.model.graph_node import Kind
        from practices.stories.model.codeql.codeql_model import Example

        populated = CodeQLStoryModel.load_content(EXPECTED / "codeql")
        expected = TypeScriptStoryModel().load(_expected_typescript())
        expect(_story_names(walk(populated))).to(equal(_story_names(walk(expected))))
        written = TypeScriptStoryModel(populated).save()
        again = TypeScriptStoryModel().load(written)
        expect(_story_names(walk(again))).to(equal(_story_names(walk(populated))))
        _expect_clean_engineering_relationships(populated)


def _expect_clean_engineering_relationships(populated) -> None:
    """Story edges that name a class, and the class-model edges those classes hold."""
    from harness.knowledge_graph.model.graph_node import Kind
    from practices.clean_engineering.model.codeql.codeql_model import OoadClass
    from practices.stories.model.codeql.codeql_model import Example

    graph = populated.graph
    linked = [
        example
        for example in graph.nodes_of_type(Example)
        if example.related(Kind.DEMONSTRATES)
    ]
    expect(len(linked) > 0).to(equal(True))
    classes = graph.nodes_of_type(OoadClass)
    expect(len(classes) > 0).to(equal(True))
    owned_members = [
        node
        for cls in classes
        for node in cls.related(Kind.OWNS)
        if node.semantic_type() in ("Operation", "Property")
    ]
    expect(len(owned_members) > 0).to(equal(True))
