"""ProjectStoryFiles. A project's story maps and story tests as the Stories practice reads them: one object holds the
practice's formats, the project every node names its file from, and who hears each file a read takes."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Callable, Optional


from cdd_guidance.practices.stories.model.code_story_map import CodeStoryMap
from cdd_guidance.practices.stories.model.story_map_files import (
    STORY_FILE_SUFFIXES,
    STORY_TESTS_FOLDER,
    StoryMapFiles,
    is_story_map_file,
    path_from,
    preferred_maps,
)
from cdd_guidance.practices.stories.model.story_map import NOT_ON_STORY_MAP, Epic, StoryMap, StoryNode
from cdd_guidance.practices.stories.model.story_recording import StorySource, StorySources

# A story test names its story map: `# Map: ../../.context/story-map.md#story` or `Map: .context/story-map.md.`
_MAP_LINE = re.compile(r"Map:\s*(\S+?\.md)\b")
# Hears each file a read takes, by its path from the project, as it is read.
OnFile = Optional[Callable[[str], None]]


class ProjectStoryFiles:
    """The story maps and story tests of one project, read by the Stories practice's formats: a folder's story map
    (``story_map_in``), the story map of files being edited (``story_map_of``), the map an edit to one file writes back
    (``opened``), each story test with the stories it holds (``story_tests``), and the sources a story test brings
    (``sources_of``). Every node names its file as a path from project."""

    def __init__(self, formats, project: Path, on_file: OnFile = None) -> None:
        self._formats = formats
        self.project = Path(project).resolve()
        self._on_file = on_file

    @property
    def code_readers(self) -> list[CodeStoryMap]:
        """The code formats the practice reads story tests in."""
        return [reader for reader in (self._formats.adapter(name) for name in self._formats) if isinstance(reader, CodeStoryMap)]

    def story_tests(self, written: list[Path]) -> dict[str, list[str]]:
        """Each story test among the written files, by its path from the project, with the names of the stories it
        holds."""
        held = {}
        for path in sorted({file.resolve() for file in written}):
            reader = self.reader_of(path)
            if reader is not None:
                held[path_from(self.project, path)] = [story.name for story in reader.story_file(path_from(self.project, path), path.read_text(encoding="utf-8"), self.project).stories]
        return held

    def take_code_scenarios(self, model: StoryMap, paths: list[Path], code_project: Path) -> None:
        """Give each story of model the scenarios the story files in code among paths hold, each file named from the
        project, each read with code_project as the folder its code imports resolve from. A story's first story file
        in code replaces the scenarios the map's markdown gave it, and each later one adds its own."""
        for path in paths:
            reader = self.reader_of(path)
            if reader is None:
                continue
            text = path.read_text(encoding="utf-8")
            file = os.path.relpath(path, self.project).replace("\\", "/")
            model.sources.take(self.sources_of(StorySource(file, text)))
            model.test_scenarios.take(reader.story_file(file, text, code_project).stories, file)

    def story_map_in(self, root: Path) -> StoryMap:
        """The story map in the folder root: the nearest story map at or above it, else its story-graph.json, else the
        markdown story maps under it, with their scenarios and increments. A map under root names its files from root,
        as a read of the files being edited names them, so the two reads place each node in the same file; a map above
        root names them from its own folder."""
        files = StoryMapFiles(root)
        nearest = files.nearest()
        if nearest is not None:
            inside = Path(root).resolve() in nearest.resolve().parents
            return self._story_map_file(nearest, Path(root) if inside else nearest.parent)
        saved = files.story_graph()
        if saved is not None:
            return self._formats.adapter("json").read_file(saved, files.folder, self._on_file)
        return self._formats.adapter("markdown").read_folder(files.folder, files.folder, self._on_file) or StoryMap()

    def story_map_of(self, files: list[Path]) -> StoryMap:
        """The story maps and story tests among files, merged into one story map whose nodes name their files as paths
        from project. The story maps among files and the map beside or named by each of the rest are read
        (``_maps_to_read``), a story test's scenarios go on the map's Story of the same name, which it specifies, and a
        story only a story test in code holds goes under the epics its folders name
        (``_take_stories_only_code_holds``), so a story test read alone has the place its map gives it. With no story
        map among files, beside them or named by them, story tests in code under a project's story_tests are the map
        themselves (``_story_map_of_code``)."""
        paths = [Path(item).resolve() for item in files]
        tests = [path for path in paths if self.reader_of(path) is not None]
        if not self._maps_to_read(paths, tests):
            from_code = self._story_map_of_code(tests)
            if from_code.epics:
                return from_code
        merged = StoryMap()
        for path in self._maps_to_read(paths, tests):
            self._take_map(merged, self._story_map_file(path, self.project))
        for path in tests:
            self._take_story_test(merged, self._read_story_test(path))
        self._take_stories_only_code_holds(merged, tests)
        return merged

    def _take_stories_only_code_holds(self, merged: StoryMap, tests: list[Path]) -> None:
        """Each story the story tests in code hold that merged has no story of the same name for, under the epics of
        merged its test's folders name, each epic added where merged has none of that name; a story's own folder,
        which the code map reads as an epic of the story's name, is not one. When merged was read from a story map,
        the story is marked as not on it, so the rule scenarios-name-a-story-on-the-map reports its story test: a
        story taken off the map would otherwise keep its test without a word."""
        held = merged.descendants.stories_by_name()
        from_a_map = bool(held)
        for story in self._story_map_of_code_unheard(tests).descendants.stories():
            if story.name not in held:
                self._epic_along(merged, story).stories.append(story)
                if from_a_map:
                    story.set_fact(NOT_ON_STORY_MAP, True)

    def _epic_along(self, merged: StoryMap, story: StoryNode) -> StoryNode:
        """The epic of merged at the epic names above story in its code map, made where merged lacks one."""
        holder: StoryNode = merged
        for code_epic in [epic for epic in self._epics_above(story) if epic.name != story.name]:
            found = next((epic for epic in holder.epics if epic.name == code_epic.name), None)
            if found is None:
                found = Epic(code_epic.name, len(holder.epics) + 1)
                found.source = code_epic.source
                holder.epics.append(found)
            holder = found
        return holder

    def _epics_above(self, story: StoryNode) -> list[StoryNode]:
        """The epics above story, from its map's top epic down."""
        above = []
        node = story.parent
        while isinstance(node, Epic):
            above.insert(0, node)
            node = node.parent
        return above

    def _maps_to_read(self, paths: list[Path], tests: list[Path]) -> list[Path]:
        """The story maps among paths, and the map beside each story test and scenarios markdown file among them, which
        reads that file's scenarios as they are now: one file per map, its markdown before its drawio
        (``preferred_maps``)."""
        maps = [path for path in paths if is_story_map_file(path)]
        scenario_files = [path for path in paths if path.suffix.lower() == ".md" and path.name.endswith(STORY_FILE_SUFFIXES)]
        return preferred_maps(maps + [found for found in self._maps_beside(tests + scenario_files) if found not in maps])

    def _take_map(self, merged: StoryMap, read: StoryMap) -> None:
        merged.sources.take(read.sources)
        for epic in list(read.epics):
            merged.epics.append(epic)

    def _read_story_test(self, path: Path) -> StorySource:
        file = path_from(self.project, path)
        if self._on_file is not None:
            self._on_file(file)
        return StorySource(file, path.read_text(encoding="utf-8"))

    def _take_story_test(self, merged: StoryMap, test: StorySource) -> None:
        """The story test's scenarios onto merged's Story of the same name, each step with the code the story test
        gives it, as a story test read with no map has it; and the story test's text and its examples modules'."""
        merged.sources.take(self.sources_of(test))
        reader = self.reader_of(self.project / test.file)
        merged.test_scenarios.take(reader.story_file(test.file, test.text, self.project).stories, test.file)

    def opened(self, path: Path):
        """The story map an edit to the Stories file at path writes back: a markdown story map or scenarios file read
        by itself (``MarkdownStoryMap.opened_from``), so a save keeps every line it does not change; a story map in
        another format read by the format that reads its extension; a story test, which is read and not edited, merged
        onto its story map (``read_files``)."""
        if self.reader_of(Path(path)) is not None:
            return self.story_map_of([path])
        return self._formats.for_file(Path(path)).opened_from(Path(path), self.project)

    def _story_map_of_code(self, tests: list[Path]) -> StoryMap:
        """The story map the story tests in code among tests hold under the project's story_tests, each language read
        by its own format: their folders are its epics and sub-epics, and their stories and scenarios its own, each
        naming its test as its file. An epic two languages both give is one epic holding the stories of both. Empty
        when none sits under story_tests."""
        return self._code_map(tests, self._on_file)

    def _story_map_of_code_unheard(self, tests: list[Path]) -> StoryMap:
        """The story map of code of tests, read again without telling on_file of each file a second time."""
        return self._code_map(tests, None)

    def _code_map(self, tests: list[Path], on_file: OnFile) -> StoryMap:
        merged = StoryMap()
        for reader, texts in self._texts_by_reader(tests).items():
            read = type(reader)(tests_root=STORY_TESTS_FOLDER).load(texts, on_file=on_file, project=self.project)
            merged.sources.take(read.sources)
            self._merge_epics(merged, read.epics)
        return merged

    def _merge_epics(self, holder: StoryNode, epics: list[Epic]) -> None:
        """Add epics under holder, a story map or an epic: one holder has no epic of the same name for is added whole;
        one it has gives that epic its stories and, the same way, its sub-epics."""
        for epic in list(epics):
            found = next((held for held in holder.epics if held.name == epic.name), None)
            if found is None:
                holder.epics.append(epic)
                continue
            for story in list(epic.stories):
                found.stories.append(story)
            self._merge_epics(found, list(epic.epics))

    def _texts_by_reader(self, tests: list[Path]) -> dict[type, dict[str, str]]:
        """Each story test's text by its path from project, grouped by the code format that reads it."""
        by_reader: dict[type, dict[str, str]] = {}
        for path in tests:
            by_reader.setdefault(self.reader_of(path), {})[path_from(self.project, path)] = path.read_text(encoding="utf-8")
        return by_reader

    def reader_of(self, path: Path):
        """The code format whose story type reads the story test at path; none for any other file."""
        return next((reader for reader in self.code_readers if reader.is_story_file(path)), None)

    def _story_map_file(self, path: Path, project: Path) -> StoryMap:
        """The story map in the file at path, read by the format that reads its extension, each node naming its file
        as a path from project."""
        return self._formats.for_file(path).read_file(path, project, self._on_file)


    def _maps_beside(self, tests: list[Path]) -> list[Path]:
        """The story map each story test belongs to: in its own folder, or the nearest folder above it inside project,
        since story tests sit in epic folders below their map; else the map its text names on a ``Map:`` line, from its
        own folder or from project, for a story test that sits beside the code rather than under its map."""
        found = [StoryMapFiles(path.parent, top=self.project).nearest() or self._named_map(path) for path in tests]
        return list(dict.fromkeys(path for path in found if path))

    def _named_map(self, test: Path) -> Path | None:
        """The story map the story test at test names on a ``Map:`` line, from its own folder or from project; none when
        it names none that is there."""
        named = _MAP_LINE.search(test.read_text(encoding="utf-8"))
        if named is None:
            return None
        relative = named.group(1).split("#", 1)[0]
        return next((path for path in (test.parent / relative, self.project / relative) if path.is_file()), None)

    def sources_of(self, test: StorySource) -> StorySources:
        """The story test, and each examples module it imports that is there under project, which an example's facts
        read its exported names from."""
        sources = StorySources()
        sources.add(test.file, test.text)
        for module in test.imported_example_files():
            if (self.project / module).is_file():
                sources.add(module, (self.project / module).read_text(encoding="utf-8"))
        return sources
