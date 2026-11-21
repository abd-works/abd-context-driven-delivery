"""How Stories takes part in the graph: it reads the story tests (or, when there are none, the story maps) into a
story model, which writes itself onto the graph, then links each step to the operations it calls and each example to
the classes and properties it shows."""

from __future__ import annotations

import os
import re
from functools import cached_property
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING

from harness.agent_tools.progress import report_progress
from harness.graph.skipped_folders import scanned_files
from harness.guidance.practice_reading import PracticeReading

from cdd_guidance.practices.clean_engineering.model.base_class_model import MODULE_FUNCTION_HOLDER
from cdd_guidance.practices.stories.model.code_story_model import CodeStoryModel
from cdd_guidance.practices.stories.model.modelled_areas import ExampleObservations, ModelledAreas
from cdd_guidance.practices.stories.model.story_recording import StorySource, imported_files
from cdd_guidance.practices.stories.model.term_links import TermLinks
from cdd_guidance.practices.stories.model.story_map_files import STORY_FILE_SUFFIXES, StoryMapFiles, is_story_map_file

if TYPE_CHECKING:
    from harness.graph.graph import Node

    from cdd_guidance.practices.stories.model.story_model import StoryModel

_MEMBER_CALL = re.compile(r"\.([\w$]+)\s*\(")
# A call by name alone, with no object before it: `seed_ticket(world)`, not `board.reread()` or `def seed_ticket(`.
_FUNCTION_CALL = re.compile(r"(?<![\w$.])(?<!def )(?<!function )([A-Za-z_$][\w$]*)\s*\(")
_STEP_TYPES = frozenset({"Step", "Given", "When", "Then"})
# What a module named through a path alias starts with: `@src/customer`, `@/customer`, `~/customer`.
_PATH_ALIAS_MARK = re.compile(r"^(?:@/|~/|@)")
# An examples module a story test imports its seeds and fixtures from, such as ticket_story_examples.py or
# customers-examples.ts: test code, which a step never invokes.
_EXAMPLES_MODULE_FILE = re.compile(r"examples\.\w+$")
# The module an examples file is imported as, its path without an extension: ./examples/account-credentials.examples.
_EXAMPLES_MODULE = re.compile(r"examples$")
# What a step's calls reach (its calls_reach fact): nothing, only the story test's own code, the code it tests, or code
# the graph has not read.
CALLS_REACH_NONE = "none"
CALLS_REACH_TEST = "test"
CALLS_REACH_TESTED = "tested"
CALLS_REACH_UNREAD = "unread"
# A story map's epic is recorded as an Epic, or as a SubEpic under another epic; a map built on a graph without being
# recorded calls every epic an Epic.
_EPIC_TYPES = frozenset({"Epic", "SubEpic"})


class StoriesReading(PracticeReading):
    """How Stories takes part in the graph: it reads the story tests under its root, through the TypeScript format
    Stories holds, or the story maps there when there are none, with edited files only what they touch; writes the
    story map onto its graph; links each Then to the examples it observes (*ExampleObservations*), each step to the
    Clean Engineering operations it calls and each example to the classes and properties it shows, and each step to
    the DDD class each of its linked domain terms names (*TermLinks*), so it reads after Clean Engineering and DDD;
    and says which areas of the map a model is written for (*ModelledAreas*), where alone a Then must observe an
    Example."""

    reads_after = ("clean_engineering", "ddd")
    source_ordered_types = frozenset({"Background", "Scenario", "Step", "Story"})
    rule_types = {
        "SubEpic": ("Epic", "StoryNode"),
        "Epic": ("StoryNode",),
        "Story": ("StoryNode",),
        "Given": ("Step",),
        "When": ("Step",),
        "Then": ("Step",),
    }
    """A step is recorded as the Given, When, or Then it is, while the schema keeps every step's rules on Step (its
    given, when, and then types are each a Step), so each carries Step's rules; its check says which kind it judges."""

    recorded_map = None
    """The story map this practice last wrote onto its graph, whose nodes its links start from."""

    @cached_property
    def story_tree(self) -> "StoryTree":
        """The story map as this practice's graph holds it, read through its edges and saved facts: what every reader of
        Stories' nodes asks for an epic's stories, a story's scenarios, or a scenario's steps."""
        return StoryTree(self)

    @property
    def root(self) -> Path:
        """The folder the practice reads its story tests and story maps from."""
        return Path(self.in_graph.source_root)

    @property
    def object_model(self) -> PracticeReading | None:
        """The part of the Clean Engineering practice the graph that holds Stories reads beside it, whose operations its
        steps call and whose classes its examples show; none when the graph reads none."""
        from cdd_guidance.practices.clean_engineering.clean_engineering import CleanEngineering

        loaded = self.graph.practices.loaded(CleanEngineering) if self.graph is not None else None
        return loaded.reading if loaded is not None else None

    @property
    def domain_model(self) -> PracticeReading | None:
        """The part of the DDD practice the graph that holds Stories reads beside it, whose aggregates its scenarios
        name; none when the graph reads none."""
        from cdd_guidance.practices.ddd.ddd import Ddd

        loaded = self.graph.practices.loaded(Ddd) if self.graph is not None else None
        return loaded.reading if loaded is not None else None

    def read_with(self, files: list[Path]) -> list[Path]:
        """Every file Stories' nodes were read from, when one of files is a story map, a scenarios file, a story test,
        or a file one of its nodes was read from: a story takes its scenarios from its story tests and its place from
        the map, so a refresh of one of them reads them all, as the load did. A refresh of any other file reads none."""
        held = self._files_held()
        if not any(path in held or self._is_story_file(path) for path in files):
            return []
        return sorted(held)

    def _files_held(self) -> set[Path]:
        """The files Stories' nodes in the graph were read from, a file that is gone since among them."""
        root = self.root.resolve()
        files = {(root / node.source.file).resolve() for node in self.in_graph.nodes() if node.source is not None and node.source.file}
        return {path for path in files if not path.is_dir()}

    def _is_story_file(self, path: Path) -> bool:
        """Whether Stories reads the file at path: a story map, a story's scenarios in markdown, or a story test in a
        code format the practice reads."""
        if is_story_map_file(path) or path.name.endswith(STORY_FILE_SUFFIXES):
            return True
        return any(reader.is_story_file(path.as_posix()) for reader in self._code_readers)

    @property
    def _code_readers(self) -> list[CodeStoryModel]:
        """The code formats the practice reads story tests in."""
        return [reader for reader in (self.practice.formats.adapter(name) for name in self.practice.formats) if isinstance(reader, CodeStoryModel)]

    def read_working_copy(self) -> None:
        """Read the story tests, or the story maps when there are none, write the story map onto its graph, and link
        each step to the operations it calls and each example to the classes and properties it shows."""
        self.recorded_map = self._story_map()
        report_progress("stories · record")
        self.recorded_map.record(self.practice, on_node=lambda detail: report_progress(f"stories · record · {detail}"))
        self._link_background_givens()
        ExampleObservations(self, self.story_tree).link()
        clean = self.object_model
        if clean is not None:
            StoryLinks(self, clean, self.story_tree).link()
        domain = self.domain_model
        if domain is not None:
            TermLinks(self, domain).link()
        ModelledAreas(self).record()

    def _link_background_givens(self) -> None:
        """Record the ``given`` edge from each background to the Given steps it holds: the step its schema says it is
        given by, which a working copy's read records itself rather than leaving it to the schema's evidence."""
        for background in self.in_graph.nodes("Background"):
            for edge in self.graph.edges.from_parent("steps", background):
                if edge.child.type == "Given":
                    self.graph.edges.relate("given", background, edge.child)

    def _story_map(self):
        model = self._story_tests()
        if model.epics:
            return model
        report_progress("stories · markdown")
        model = self._story_maps()
        if not self._reads_markdown_scenarios:
            model.test_scenarios.drop()
            self._take_code_scenarios(model)
        elif self.graph.scope.edited_files is None:
            # A read of named files gave each story its story tests' scenarios already; a read of the whole folder
            # read only the map and its markdown, so the story tests in code are taken here.
            self._take_code_scenarios(model)
        return model

    @property
    def _reads_markdown_scenarios(self) -> bool:
        """Whether the fidelity the practice works at lists markdown among the formats it writes: a story test written in
        markdown is read only there. Code is a format of every fidelity, so a fidelity that lists no markdown reads its
        scenarios from code alone; with no fidelity, every format is read."""
        current = self.practice.fidelities.current
        return current is None or "markdown" in current.outputs

    def _take_code_scenarios(self, model: "StoryModel") -> None:
        """Give each story of model the scenarios its story files in code under the root hold, in each code format the
        practice reads: its story tests, its shared stories, and its screen specs, by the files each format names its
        story files; with edited files, only those among them. A story's first story file in code replaces the
        scenarios the map's markdown gave it, and each later one adds its own, as a read of named files gives them."""
        readers = self._code_readers
        suffixes = {Path(suffix).suffix for reader in readers for suffix in reader.story_file_suffixes}
        edited = self.graph.scope.edited_files
        project = Path(self.graph.scope.folder) if self.graph.scope.folder is not None else self.root
        for path in self._scanned(suffixes):
            reader = next((reader for reader in readers if reader.is_story_file(path.as_posix())), None)
            if reader is None or (edited is not None and path not in edited):
                continue
            text = path.read_text(encoding="utf-8")
            file = os.path.relpath(path, self.root).replace("\\", "/")
            model.sources.add(file, text)
            model.test_scenarios.take(reader.stories_of(text, file, project)[0], file)

    def _story_tests(self) -> "StoryModel":
        files = self._typescript_texts()
        report_progress("stories · parse")
        return self.practice.formats.adapter("typescript").parse(files, on_file=lambda detail: report_progress(f"stories · parse · {detail}"))

    def _typescript_texts(self) -> dict[str, str]:
        """The text of each TypeScript file the story tests are read from, by its path from the root."""
        sources = self._typescript_files()
        files: dict[str, str] = {}
        for index, path in enumerate(sources, start=1):
            relative = os.path.relpath(path, self.root).replace("\\", "/")
            report_progress(f"stories · {index}/{len(sources)} · {relative}")
            files[relative] = path.read_text(encoding="utf-8")
        return files

    def _story_maps(self):
        """The story maps under the practice's root; with edited files, only the story maps among them."""
        on_file = lambda detail: report_progress(f"stories · markdown · {detail}")  # noqa: E731
        edited = self.graph.scope.edited_files
        if edited is None:
            return self.practice.read_folder(self.root, on_file=on_file)
        return self.practice.read_files(edited, self.root, on_file=on_file)

    def _scanned(self, suffixes: set[str]) -> list[Path]:
        """The files with suffixes in the folders the practice's story files sit in: its root and, for a root that is a
        project's .context, the story_tests beside it."""
        return [path for folder in StoryMapFiles(self.root).story_folders() for path in scanned_files(folder, suffixes)]

    def _typescript_files(self) -> list[Path]:
        """TypeScript under the root; with edited files, each whole story folder that holds one. A story reads its
        examples and steps from sibling files, so one edited file needs its story's other files."""
        edited = self.graph.scope.edited_files
        if edited is not None and not any(path.suffix.lower() in {".ts", ".tsx"} for path in edited):
            return []
        found = self._scanned({".ts", ".tsx"})
        if edited is None:
            return found
        reader = self.practice.formats.adapter("typescript")
        stories = {path.parent for path in found if reader.is_story_file(path.as_posix())}
        stories = {story for story in stories if any(story == file.parent or story in file.parents for file in edited)}
        return [path for path in found if path in edited or any(story in path.parents for story in stories)]


class StoryTree:
    """The story map as the graph holds it: each epic's sub-epics and stories, each story's scenarios, each scenario's
    steps, and the epic above any of them, read through the edges Stories records and the facts each node saves. It
    answers the same for the objects a read parsed and for the plain nodes of a graph opened from its save, so every
    reader of Stories' nodes, in this practice or another, asks it rather than a parsed object's attributes."""

    def __init__(self, stories: PracticeReading) -> None:
        self.stories = stories

    def epic_of(self, node: "Node") -> "Node | None":
        """The epic of the story map whose tree holds node, the outermost found up the graph's own edges; none for a
        node under no epic."""
        epic = None
        above = self.stories.graph.edges.direct_parent(node)
        while above is not None:
            epic = above if above.type in _EPIC_TYPES else epic
            above = self.stories.graph.edges.direct_parent(above)
        return epic

    def sub_epics(self, epic: "Node") -> list["Node"]:
        """The sub-epics directly under epic, in the order the map lists them."""
        return self._below(epic, "decomposedInto", _EPIC_TYPES)

    def stories_under(self, epic: "Node") -> list["Node"]:
        """The stories directly under epic or a sub-epic, in the order the map lists them."""
        return self._below(epic, "decomposedInto", {"Story"})

    def scenarios(self, story: "Node") -> list["Node"]:
        """The story's scenarios, in the order its story test or map lists them."""
        return self._below(story, "scenarios", {"Scenario"})

    def steps(self, scenario: "Node") -> list["Node"]:
        """The scenario's own steps, without the steps chained onto them, in order."""
        return [edge.child for edge in self.stories.graph.edges.from_parent("steps", scenario)]

    def _below(self, parent: "Node", kind: str, node_types: frozenset[str] | set[str]) -> list["Node"]:
        return [edge.child for edge in self.stories.graph.edges.from_parent(kind, parent) if edge.child.type in node_types]


class ImportedFiles:
    """The files a story file's steps can call code in: the files its imports name and the files those import in turn, found
    in the project the graph reads. A step invokes an operation only in one of them, so an operation of the same name
    in a module the story file never imports, or in another language, is not one it calls. A module named from a
    package root is looked for under each folder above the importing file, with the mark a path alias starts with
    (``@src/customer``, ``@/customer``, ``~/customer``) taken off. Each file's imports are read once."""

    def __init__(self, stories_root: Path, project: Path | None) -> None:
        self._stories_root = stories_root.resolve()
        project = project.resolve() if project is not None else None
        inside = project is not None and (project == self._stories_root or project in self._stories_root.parents)
        # The folder files are named from: the project, or the folder Stories reads when that lies outside it.
        self._project = project if inside else self._stories_root
        self._imports: dict[str, list[str]] = {}
        self._reached: dict[str, set[Path]] = {}
        self._texts: dict[str, str] = {}

    def reached_from(self, step: "Node") -> set[Path]:
        """Every file the story file of step imports, straight or through the files it imports; the story file's own
        imports come from the facts its nodes keep, the others' from their text."""
        file = self._named_from_project(step)
        if file not in self._reached:
            modules = step.get_fact("imported_modules") or {}
            self._imports.setdefault(file, self._imported(file, modules))
            reached = self._closure(file) | self._package_files(file, modules)
            self._reached[file] = {(self._project / found).resolve() for found in reached}
        return self._reached[file]

    def text_of(self, step: "Node") -> str:
        """The text of step's story file as it is on disk, read once; empty when the file is gone."""
        file = self._named_from_project(step)
        if file not in self._texts:
            path = self._project / file
            self._texts[file] = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
        return self._texts[file]

    def _named_from_project(self, step: "Node") -> str:
        return (self._stories_root / step.source.file).relative_to(self._project).as_posix()

    def _package_files(self, file: str, modules: dict[str, str]) -> set[str]:
        """The files, in file's own language, of each package file imports a module of: a story file that imports
        only a seed or an example from the package of the code it tests gets that package's objects from it, so the
        package is in its reach. A module named with no folder, such as the story-test library, names no package."""
        suffix = PurePosixPath(file).suffix
        unaliased = {name: _PATH_ALIAS_MARK.sub("", module) for name, module in modules.items() if "/" in module.lstrip("./")}
        folders = {PurePosixPath(found).parent for found in imported_files(file, unaliased)}
        return {
            path.relative_to(self._project).as_posix()
            for folder in folders if (self._project / folder).is_dir()
            for path in (self._project / folder).iterdir() if path.is_file() and path.suffix == suffix
        }

    def _closure(self, file: str) -> set[str]:
        found: set[str] = set()
        pending = [file]
        while pending:
            for imported in self._imported_by(pending.pop()):
                if imported not in found:
                    found.add(imported)
                    pending.append(imported)
        return found

    def _imported_by(self, file: str) -> list[str]:
        if file not in self._imports:
            text = (self._project / file).read_text(encoding="utf-8", errors="replace")
            self._imports[file] = self._imported(file, StorySource(file, text).imported_modules)
        return self._imports[file]

    def _imported(self, file: str, modules: dict[str, str]) -> list[str]:
        """The files of the project that file imports modules from."""
        unaliased = {name: _PATH_ALIAS_MARK.sub("", module) for name, module in modules.items()}
        return [found for found in imported_files(file, unaliased) if (self._project / found).is_file()]


class StoryLinks:
    """The edges between the Stories practice and Clean Engineering: a step invokes the operations it calls, an epic
    uses the modules those operations sit in, and an example demonstrates the classes it names and retrieves the
    properties it reads. Each is read from the facts every step and example saves with the graph (its body's text, the
    names its source holds) and from the graph's own edges, never from the parsed object behind a node: a refresh in a
    worker process holds the steps and examples it did not read again as plain nodes, and links them the same way."""

    def __init__(self, stories: PracticeReading, clean: PracticeReading, tree: "StoryTree") -> None:
        self.stories = stories
        self.clean = clean
        self.tree = tree
        self.graph = stories.graph
        self.imported_files = ImportedFiles(Path(stories.in_graph.source_root), self.graph.scope.folder)

    @cached_property
    def modules(self) -> set:
        """Clean Engineering's modules, read from the graph once."""
        return set(self.clean.in_graph.nodes("Module"))

    @cached_property
    def examples(self) -> list:
        """The examples on the Stories graph, read once."""
        return self.stories.in_graph.nodes("Example")

    def link(self) -> None:
        steps = [node for node in self.stories.in_graph.nodes() if node.type in _STEP_TYPES]
        for index, step in enumerate(steps, start=1):
            report_progress(f"stories · steps · {index}/{len(steps)} · {step.name}")
            self._link_step(step)
        for index, example in enumerate(self.examples, start=1):
            report_progress(f"stories · examples · {index}/{len(self.examples)} · {example.name}")
            self._link_example(example)

    @cached_property
    def story_files(self) -> set[str]:
        """The files the Stories practice read its story map and story tests from, read once: test code."""
        return {node.source.file for node in self.stories.in_graph.nodes() if node.source is not None and node.source.file}

    def _is_tested_code(self, member: "Node") -> bool:
        """True for Clean Engineering code a step can invoke: never a function of a story test, such as a helper
        its steps call, nor of the examples module it takes its seeds from."""
        file = member.source.file if member.source is not None else ""
        return bool(file) and file not in self.story_files and not _EXAMPLES_MODULE_FILE.search(file)

    def _calls_reach(self, step: "Node", called: set, matched: list) -> str:
        """What a step's calls reach, recorded as its ``calls_reach`` fact for the rule code-steps-invoke-code: ``none``
        when it calls nothing, ``tested`` when one call reaches the code under test, ``test`` when every call is a story
        test's own helper or a seed its examples module exports (whether or not that module was read), and ``unread``
        when a call names code the graph has not read."""
        if not called:
            return CALLS_REACH_NONE
        if any(self._is_tested_code(member) for member in matched):
            return CALLS_REACH_TESTED
        imported = step.get_fact("imported_modules") or {}
        seeds = {name for name, module in imported.items() if _EXAMPLES_MODULE.search(str(module))}
        resolved = {member.name for member in matched}
        return CALLS_REACH_UNREAD if called - resolved - seeds else CALLS_REACH_TEST

    def _link_step(self, step: "Node") -> None:
        body = self._step_body(step)
        called = set(step.get_fact("callees") or []) | set(_MEMBER_CALL.findall(body))
        matched = [member for name in sorted(called) for member in self.clean.code_index.members_named(name)]
        matched += [function for function in self._functions_called(body) if function not in matched]
        matched = self._of_known_receiver(step, body, [member for member in matched if self._can_call(step, member)])
        step.set_fact("calls_reach", self._calls_reach(step, called | set(_FUNCTION_CALL.findall(body)), matched))
        matched = [member for member in matched if self._is_tested_code(member)]
        epic = self.tree.epic_of(step) if matched else None
        for operation in matched:
            self.graph.edges.relate("invokes", step, operation)
            self.graph.edges.relate("invokedBy", operation, step)
            module = self._module_of(operation)
            if module is not None and epic is not None:
                self.graph.edges.relate("usedBy", module, epic)
                self.graph.edges.relate("uses", epic, module)

    def _of_known_receiver(self, step: "Node", body: str, members: list["Node"]) -> list["Node"]:
        """members, keeping of the operations and properties several classes in reach declare under one name only the
        one of the class the story file built the call's receiver as (``self.board = Board()``); when no line of the
        file says which class the receiver is, none of them, since the name alone does not say which is called. A
        name one class declares, and a module's function, stay."""
        owners: dict[str, set[tuple[str, str]]] = {}
        for member in members:
            if member.get_fact("owner") != MODULE_FUNCTION_HOLDER:
                owners.setdefault(member.name, set()).add((member.source.file, member.get_fact("owner")))
        shared = {name for name, declaring in owners.items() if len(declaring) > 1}
        if not shared:
            return members
        built = {name: self._classes_built_for(step, body, name) for name in shared}
        return [member for member in members if member.name not in shared or member.get_fact("owner") in built[member.name]]

    def _classes_built_for(self, step: "Node", body: str, name: str) -> set[str]:
        """The class names step's story file builds each receiver of a call to name in body as."""
        text = self.imported_files.text_of(step)
        receivers = set(re.findall(rf"((?:[\w$]+\.)*[\w$]+)\.{re.escape(name)}\s*\(", body))
        built = (re.search(rf"(?<![\w$.]){re.escape(receiver)}\s*(?::[^=\n]+)?=\s*(?:new\s+)?([A-Za-z_$][\w$]*)\s*\(", text) for receiver in receivers)
        return {found.group(1) for found in built if found is not None}

    def _can_call(self, step: "Node", member: "Node") -> bool:
        """Whether step's story file can call member: member sits in that file, in a file it imports, straight or
        through the files it imports, or in a package it imports a module of. A call is never joined to an operation
        on its name alone."""
        if member.source is None or not member.source.file:
            return False
        if member.source.file == step.source.file:
            return True
        return (self._clean_root / member.source.file).resolve() in self.imported_files.reached_from(step)

    @cached_property
    def _clean_root(self) -> Path:
        """The folder Clean Engineering's nodes name their files from."""
        return Path(self.clean.in_graph.source_root).resolve()

    def _link_example(self, example: "Node") -> None:
        names = set(example.get_fact("source_names") or [])
        reads = set(example.get_fact("source_reads") or [])
        for class_node in self.clean.in_graph.nodes("OoadClass"):
            if class_node.name in names:
                self.graph.edges.group("demonstrates", example, class_node)
                self.graph.edges.group("demonstrates", class_node, example)
                self.graph.edges.relate("demonstratedThrough", class_node, example)
        for prop in self.clean.in_graph.nodes("Property"):
            if prop.name in reads:
                self.graph.edges.relate("retrievedUsing", example, prop)
                self.graph.edges.relate("retrievedUsing", prop, example)

    def _functions_called(self, body: str) -> list:
        """The functions body calls by name, such as a Python story test's ``seed_ticket(world)``: only a function of a
        module answers a bare call, never a class's operation, which is called on an object."""
        names = sorted(set(_FUNCTION_CALL.findall(body)))
        return [member for name in names for member in self.clean.code_index.members_named(name) if member.get_fact("owner") == MODULE_FUNCTION_HOLDER]

    def _step_body(self, step: "Node") -> str:
        """The step's own text and the body its story test gives it."""
        return f"{step.name}\n{step.get_fact('body_text') or ''}"

    def _module_of(self, operation: "Node") -> "Node | None":
        """The Clean Engineering module that holds the operation: the nearest module above it in the graph."""
        owner = self.graph.edges.direct_parent(operation)
        while owner is not None and owner not in self.modules:
            owner = self.graph.edges.direct_parent(owner)
        return owner
