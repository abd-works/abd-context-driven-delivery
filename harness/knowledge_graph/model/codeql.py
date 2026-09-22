"""CodeQL collaborator — database, queries, and graph populate."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from practices.clean_engineering.model.operation import Parameter as SourceParameter
from practices.ddd.model.stereotypes import ddd_class_kind
from practices.stories.model.scenario import Phase
from practices.stories.model.source_location import SourceLocation

from practices.clean_engineering.model.codeql.clean_engineering import (
    CleanEngineeringModel,
    Module,
    OoadClass,
    Operation,
    Property,
)
from practices.ddd.model.codeql.ddd import ddd_graph_class_for
from practices.stories.model.codeql.stories import (
    Background,
    Epic,
    Example,
    Scenario,
    Step,
    Story,
    StoryMap,
    SubEpic,
)
from .graph_node import Kind, Node

if TYPE_CHECKING:
    from .practice_graph import PracticeGraph

_CODEQL_QUERIES = (
    Path(__file__).resolve().parents[3]
    / "practices"
    / "clean_engineering"
    / "model"
    / "codeql"
)


class CodeQLRunError(RuntimeError):
    """CodeQL CLI was missing, the database was missing, or the query failed."""


class Rows(list):
    """Decoded CodeQL select tuples as dict rows."""


class CodeQL:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    @property
    def database(self) -> Path:
        return self.ensure_database()

    def executable(self) -> str:
        path = shutil.which("codeql")
        if path is None:
            raise CodeQLRunError("codeql is not on PATH")
        return path

    def repo_root(self) -> Path:
        for candidate in (self.root.resolve(), *self.root.resolve().parents):
            if (candidate / ".git").exists() and (candidate / "practices").is_dir():
                return candidate
        return self.root.resolve()

    def ensure_database(self, language: str = "python") -> Path:
        repo = self.repo_root()
        database = repo / ".codeql" / f"{language}-db"
        if self._database_ready(database):
            return database
        database.parent.mkdir(parents=True, exist_ok=True)
        run = subprocess.run(
            [
                self.executable(),
                "database",
                "create",
                str(database),
                f"--language={language}",
                f"--source-root={repo}",
                "--command=echo skip",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if run.returncode != 0 or not self._database_ready(database):
            raise CodeQLRunError(
                f"codeql database create failed for {repo}: {run.stderr or run.stdout}"
            )
        return database

    def class_rows(self, tuples: List[list] | None = None) -> Rows:
        database = self.ensure_database("python")
        if tuples is None:
            tuples = self.run_query_tuples(_CODEQL_QUERIES / "classes.ql", database)
        return Rows(
            {
                "name": self._cell(row, 0),
                "module": self._cell(row, 1),
                "file": self._cell(row, 2),
                "line": self._int_cell(row, 3),
            }
            for row in tuples
            if self._cell(row, 0)
        )

    def operation_rows(self, tuples: List[list] | None = None) -> Rows:
        database = self.ensure_database("python")
        if tuples is None:
            tuples = self.run_query_tuples(_CODEQL_QUERIES / "operations.ql", database)
        return Rows(
            {
                "class_name": self._cell(row, 0),
                "name": self._cell(row, 1),
                "return_type": self._cell(row, 2),
                "line": self._int_cell(row, 3),
            }
            for row in tuples
            if self._cell(row, 0) and self._cell(row, 1)
        )

    def parameter_rows(self, tuples: List[list] | None = None) -> Rows:
        database = self.ensure_database("python")
        if tuples is None:
            tuples = self.run_query_tuples(_CODEQL_QUERIES / "parameters.ql", database)
        return Rows(
            {
                "class_name": self._cell(row, 0),
                "operation": self._cell(row, 1),
                "name": self._cell(row, 2),
                "line": self._int_cell(row, 3),
            }
            for row in tuples
            if self._cell(row, 0) and self._cell(row, 1) and self._cell(row, 2)
        )

    def property_rows(self, tuples: List[list] | None = None) -> Rows:
        database = self.ensure_database("python")
        if tuples is None:
            tuples = self.run_query_tuples(_CODEQL_QUERIES / "properties.ql", database)
        return Rows(
            {
                "class_name": self._cell(row, 0),
                "name": self._cell(row, 1),
                "module": self._cell(row, 2),
                "line": self._int_cell(row, 3),
            }
            for row in tuples
            if self._cell(row, 0) and self._cell(row, 1)
        )

    def call_rows(self, tuples: List[list] | None = None) -> Rows:
        database = self.ensure_database("python")
        if tuples is None:
            tuples = self.run_query_tuples(_CODEQL_QUERIES / "calls.ql", database)
        return Rows(
            {
                "caller_class": self._cell(row, 0),
                "caller_operation": self._cell(row, 1),
                "callee_class": self._cell(row, 2),
                "callee_operation": self._cell(row, 3),
                "callee_module": self._cell(row, 4),
                "caller_module": self._cell(row, 5),
            }
            for row in tuples
            if self._cell(row, 0) and self._cell(row, 1) and self._cell(row, 2) and self._cell(row, 3)
        )

    def results_path(self, override: Optional[Path] = None) -> Optional[Path]:
        if override is not None:
            candidate = Path(override).resolve()
            return candidate if candidate.is_file() else None
        for relative in (
            ".codeql/results/practice-graph.json",
            ".codeql/results/practice-graph.bqrs.json",
        ):
            candidate = self.root / relative
            if candidate.is_file():
                return candidate
        return None

    def run(self, query: Path, database: Path | None = None) -> Rows:
        self._write_subject_filter(query.parent)
        db = database if database is not None else self.ensure_database(self._query_language(query))
        return Rows(self._select_rows(self.run_query_tuples(query, db)))

    def run_queries(self, queries: List[Path], database: Path | None = None) -> Dict[str, List[list]]:
        if not queries:
            return {}
        db = database if database is not None else self.ensure_database("python")
        run = subprocess.run(
            [
                self.executable(),
                "database",
                "run-queries",
                str(db),
                "--",
                *[str(query.resolve()) for query in queries],
            ],
            check=False,
            capture_output=True,
            text=True,
            cwd=str(self.repo_root()),
        )
        if run.returncode != 0:
            raise CodeQLRunError(
                f"codeql database run-queries failed: {run.stderr or run.stdout}"
            )
        return {query.stem: self._decode_bqrs(self._bqrs_for(db, query)) for query in queries}

    def run_query_tuples(self, ql_path: Path, database: Path) -> List[list]:
        return self.run_queries([ql_path], database)[ql_path.stem]

    def _bqrs_for(self, database: Path, query: Path) -> Path:
        results = database / "results"
        matches = list(results.rglob(f"{query.stem}.bqrs")) if results.is_dir() else []
        if not matches:
            raise CodeQLRunError(f"no bqrs for {query.stem} under {results}")
        return max(matches, key=lambda p: p.stat().st_mtime)

    def _decode_bqrs(self, bqrs: Path) -> List[list]:
        with tempfile.TemporaryDirectory() as folder:
            decoded = Path(folder) / "results.json"
            decode = subprocess.run(
                [
                    self.executable(),
                    "bqrs",
                    "decode",
                    str(bqrs),
                    "--format=json",
                    f"--output={decoded}",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if decode.returncode != 0 or not decoded.is_file():
                raise CodeQLRunError(
                    f"codeql bqrs decode failed for {bqrs}: {decode.stderr or decode.stdout}"
                )
            payload = json.loads(decoded.read_text(encoding="utf-8"))
        return payload.get("#select", {}).get("tuples", [])

    def _write_subject_filter(self, pack_dir: Path) -> None:
        repo = self.repo_root()
        try:
            prefix = self.root.resolve().relative_to(repo).as_posix().rstrip("/")
        except ValueError:
            prefix = ""
        if prefix:
            path_body = (
                "  exists(File f, string prefix, string normalized |\n"
                "    subjectFilterPrefix(prefix) and\n"
                "    path = f.getRelativePath() and\n"
                '    normalized = path.replaceAll("\\\\", "/") and\n'
                '    (normalized = prefix or normalized.matches(prefix + "/%"))\n'
                "  )\n"
            )
        else:
            path_body = (
                "  exists(File f |\n"
                '    path = f.getRelativePath().replaceAll("\\\\", "/")\n'
                "  )\n"
            )
        (pack_dir / "subject_filter.qll").write_text(
            "import python\n\n"
            f'predicate subjectFilterPrefix(string prefix) {{ prefix = "{prefix}" }}\n\n'
            "predicate inSubject(AstNode n) {\n"
            "  inSubjectPath(n.getLocation().getFile().getRelativePath())\n"
            "}\n\n"
            "predicate inSubjectFilter(Class cls) {\n"
            "  inSubject(cls)\n"
            "}\n\n"
            "predicate inSubjectPath(string path) {\n"
            f"{path_body}"
            "}\n",
            encoding="utf-8",
        )

    def _query_language(self, ql_path: Path) -> str:
        text = ql_path.read_text(encoding="utf-8")
        if "import javascript" in text:
            return "javascript"
        return "python"

    def _database_ready(self, database: Path) -> bool:
        return database.is_dir() and any(database.iterdir())

    def _cell(self, row: list, index: int) -> str:
        if index >= len(row):
            return ""
        item = row[index]
        if isinstance(item, dict):
            return str(item.get("label", ""))
        return str(item)

    def _int_cell(self, row: list, index: int) -> int:
        raw = self._cell(row, index)
        try:
            return int(raw)
        except ValueError:
            return 0

    def _entity_name(self, item) -> str:
        raw = item.get("label", item) if isinstance(item, dict) else str(item)
        text = str(raw)
        for prefix in ("Class ", "Function ", "Module ", "File ", "Script "):
            if text.startswith(prefix):
                return text[len(prefix) :]
        return text

    def _select_rows(self, tuples: List[list]) -> List[dict]:
        rows: List[dict] = []
        for item in tuples:
            if not item:
                continue
            message = item[1] if len(item) > 1 else ""
            if isinstance(message, dict):
                message = message.get("label", "")
            row = {"name": self._entity_name(item[0]), "message": str(message)}
            if len(item) > 2:
                contributor = self._entity_name(item[2])
                if contributor:
                    row["contributor"] = contributor
            rows.append(row)
        return rows


    def populate(
        self,
        graph: PracticeGraph,
        *,
        results_path: str | Path | None = None,
    ) -> None:
        database = self.ensure_database("python")
        self._write_subject_filter(_CODEQL_QUERIES)
        populate_queries = [
            _CODEQL_QUERIES / "classes.ql",
            _CODEQL_QUERIES / "operations.ql",
            _CODEQL_QUERIES / "parameters.ql",
            _CODEQL_QUERIES / "properties.ql",
            _CODEQL_QUERIES / "calls.ql",
        ]
        print(f"run-queries populate ({len(populate_queries)} queries) ...", flush=True)
        started = time.perf_counter()
        batch = self.run_queries(populate_queries, database)
        seconds = time.perf_counter() - started
        graph.record_rule_timing("run-queries:knowledge-graph", seconds, len(batch.get("classes") or []))
        print(f"run-queries populate  {seconds:.2f}s", flush=True)
        class_rows = list(self.class_rows(batch["classes"]))
        operation_rows = list(self.operation_rows(batch["operations"]))
        property_rows = list(self.property_rows(batch["properties"]))
        parameter_rows = list(self.parameter_rows(batch["parameters"]))
        call_rows = list(self.call_rows(batch["calls"]))
        raw = self._optional_json(results_path)
        if raw:
            class_rows = class_rows + list(raw.get("classes") or [])
            operation_rows = operation_rows + list(raw.get("operations") or [])
            property_rows = property_rows + list(raw.get("properties") or [])
            call_rows = call_rows + list(raw.get("calls") or [])
        if not class_rows and not (raw and (raw.get("stories") or raw.get("steps"))):
            raise RuntimeError(f"CodeQL returned no classes or stories for {self.root}")
        self._ensure_ce_nodes(graph, class_rows, property_rows, operation_rows, parameter_rows)
        self._wire_calls(graph, self._calls_within_depth(call_rows, 3))
        if raw:
            self._ensure_story_nodes(graph, raw)
            self._wire_story_calls(graph, raw.get("story_calls") or [])
            self._wire_story_observations(graph, raw.get("story_observations") or [])
            self._wire_example_demonstrates(graph, raw.get("example_exports") or [])


    def _optional_json(self, results_path) -> Optional[dict]:
        path = self.results_path(Path(results_path) if results_path else None)
        if path is None:
            return None
        return json.loads(path.read_text(encoding="utf-8"))


    def _ensure_ce_nodes(self, 
        graph: PracticeGraph,
        class_rows: List[dict],
        property_rows: List[dict],
        operation_rows: List[dict],
        parameter_rows: List[dict] | None = None,
    ) -> None:
        if class_rows and graph.ce_model is None:
            graph.ce_model = CleanEngineeringModel("CleanEngineering", 1)
            graph.register(graph.ce_model)

        modules: Dict[str, Module] = {
            mod.name.lower(): mod for mod in graph.nodes_of_type(Module)
        }
        classes: Dict[str, OoadClass] = {}
        for cls in graph.nodes.values():
            if isinstance(cls, OoadClass):
                classes[cls.name.lower()] = cls

        order = 1
        for entry in class_rows:
            module_name = entry.get("module") or ""
            name = entry.get("name") or ""
            if not name:
                continue
            mod = modules.get(module_name.lower())
            if mod is None:
                mod = graph.ce_model.load_module(Module(module_name, order))
                order += 1
                graph.register(mod)
                modules[module_name.lower()] = mod
                if graph.ce_model is not None:
                    graph.ce_model.modules.append(mod)
                    graph.ce_model.relate(Kind.OWNS, mod)

            if name.lower() in classes:
                continue
            stereotypes = entry.get("stereotypes") or []
            decorated = name
            if stereotypes:
                decorated = f"{name} {' '.join(f'<<{s}>>' for s in stereotypes)}"
            stub = OoadClass(decorated, len(mod.classes) + 1)
            if stereotypes or ddd_class_kind(decorated):
                cls = ddd_graph_class_for(stub)
            else:
                cls = mod.load_class(stub)
            mod.classes.append(cls)
            classes[name.lower()] = cls
            graph.register(cls)
            mod.relate(Kind.OWNS, cls)
            cls.relate(Kind.BELONGS_TO, mod)

        for prop in property_rows:
            cls = classes.get((prop.get("class_name") or "").lower())
            if cls is None:
                continue
            if any(p.name == prop.get("name") for p in cls.property_nodes):
                continue
            if not cls.property_nodes and cls.properties:
                cls.sync_tree_from_legacy()
            node = cls.load_property(
                Property(
                    prop.get("name") or "",
                    len(cls.property_nodes) + 1,
                    type_hint=prop.get("type_hint") or "",
                )
            )
            cls.property_nodes.append(node)
            graph.register(node)
            cls.relate(Kind.OWNS, node)
            node.relate(Kind.BELONGS_TO, cls)
            target = graph.class_named( (prop.get("type_hint") or "").split("|")[0].strip().rstrip("[]"))
            if target is not None:
                node.relate(Kind.HAS_TYPE, target)

        for op in operation_rows:
            cls = classes.get((op.get("class_name") or "").lower())
            if cls is None:
                continue
            if any(o.name == op.get("name") for o in cls.operation_nodes):
                continue
            if not cls.operation_nodes and cls.operations:
                cls.sync_tree_from_legacy()
            node = cls.load_operation(
                Operation(
                    op.get("name") or "",
                    len(cls.operation_nodes) + 1,
                    return_type=op.get("return_type") or "",
                )
            )
            node._legacy_parameters = list(op.get("parameters") or [])
            if hasattr(node, "_sync_parameters_from_legacy"):
                node._sync_parameters_from_legacy()
            cls.operation_nodes.append(node)
            graph.register(node)
            cls.relate(Kind.OWNS, node)
            node.relate(Kind.BELONGS_TO, cls)
            ret = graph.class_named( (op.get("return_type") or "").split("|")[0].strip().rstrip("[]"))
            if ret is not None:
                node.relate(Kind.RETURNS, ret)

        self._attach_parameters(graph, classes, parameter_rows or [])


    def _ensure_story_nodes(self, graph: PracticeGraph, raw: dict) -> None:
        if graph.story_map is None:
            graph.story_map = StoryMap()
            graph.register(graph.story_map)
        story_map = graph.story_map

        epics: Dict[str, Epic] = {Node.slug(e.name): e for e in graph.nodes_of_type(Epic)}
        subs: Dict[Tuple[str, str], SubEpic] = {}
        for sub in graph.nodes_of_type(SubEpic):
            parent = ""
            for epic in epics.values():
                if sub in epic.sub_epics:
                    parent = Node.slug(epic.name)
                    break
            subs[(parent, Node.slug(sub.name))] = sub
        stories: Dict[str, Story] = {Node.slug(s.name): s for s in graph.nodes_of_type(Story)}

        for entry in raw.get("stories") or []:
            epic_name = self._display(entry.get("epic") or "") or "Stories"
            sub_name = self._display(entry.get("sub_epic") or "")
            epic = epics.get(Node.slug(epic_name))
            if epic is None:
                epic = story_map.load_epic(Epic(epic_name, len(epics) + 1))
                story_map.epics.append(epic)
                graph.register(epic)
                story_map.relate(Kind.OWNS, epic)
                epics[Node.slug(epic_name)] = epic
            parent: Epic | SubEpic = epic
            if sub_name:
                key = (Node.slug(epic_name), Node.slug(sub_name))
                sub = subs.get(key)
                if sub is None:
                    sub = epic.load_sub_epic(SubEpic(sub_name, len(epic.sub_epics) + 1))
                    epic.sub_epics.append(sub)
                    graph.register(sub)
                    epic.relate(Kind.OWNS, sub)
                    subs[key] = sub
                parent = sub
            if Node.slug(entry.get("name") or "") in stories:
                story = stories[Node.slug(entry.get("name") or "")]
            elif isinstance(parent, SubEpic):
                story = parent.load_story(
                    Story(entry.get("name") or "", len(parent.stories) + 1)
                )
                story.source = SourceLocation(entry.get("file") or "", int(entry.get("line") or 0))
                parent.stories.append(story)
                graph.register(story)
                parent.relate(Kind.OWNS, story)
                stories[Node.slug(story.name)] = story
            else:
                story = Story(entry.get("name") or "", len(getattr(parent, "stories", []) or []) + 1)
                story.source = SourceLocation(entry.get("file") or "", int(entry.get("line") or 0))
                graph.register(story)
                parent.relate(Kind.OWNS, story)
                stories[Node.slug(story.name)] = story

        backgrounds: List[Tuple[dict, Background]] = []
        for entry in raw.get("backgrounds") or []:
            story = stories.get(Node.slug(entry.get("story") or ""))
            if story is None or story.backgrounds:
                continue
            background = story.load_background(
                Background(entry.get("name") or "background", 1)
            )
            story.backgrounds.append(background)
            graph.register(background)
            story.relate(Kind.OWNS, background)
            backgrounds.append((entry, background))

        scenarios: Dict[Tuple[str, str, str], Scenario] = {}
        for entry in raw.get("scenarios") or []:
            story = stories.get(Node.slug(entry.get("story") or ""))
            if story is None:
                continue
            key = (self._norm_file(entry.get("file") or ""), Node.slug(entry.get("story") or ""), (entry.get("name") or "").lower())
            scenario = story.load_scenario(
                Scenario(entry.get("name") or "", len(story.scenarios) + 1, story.name)
            )
            scenario.source = SourceLocation(entry.get("file") or "", int(entry.get("line") or 0))
            story.scenarios.append(scenario)
            graph.register(scenario)
            story.relate(Kind.OWNS, scenario)
            scenarios[key] = scenario

        created_steps: List[Tuple[dict, Step]] = []
        for entry in raw.get("steps") or []:
            parent = self._step_owner(scenarios, backgrounds, entry)
            if parent is None:
                continue
            phase = self._phase_for(entry.get("phase") or "", entry.get("keyword") or "")
            is_continuation = entry.get("keyword") in {"And", "But"}
            order = len(parent.steps) + 1 if hasattr(parent, "steps") else 1
            step = parent.load_step(
                Step(
                    text=entry.get("text") or "",
                    phase=phase,
                    sequential_order=order,
                    is_continuation=is_continuation,
                    keyword=entry.get("keyword") or "",
                    source=SourceLocation(entry.get("file") or "", int(entry.get("line") or 0)),
                )
            )
            parent.steps.append(step)
            graph.register(step)
            parent.relate(Kind.OWNS, step)
            created_steps.append((entry, step))

        self._ensure_examples(graph, raw.get("example_exports") or [], epics, subs, stories)
        self._wire_step_demonstrated_through(graph, created_steps)


    def _ensure_examples(self, 
        graph: PracticeGraph,
        entries: List[dict],
        epics: Dict[str, Epic],
        subs: Dict[Tuple[str, str], SubEpic],
        stories: Dict[str, Story],
    ) -> None:
        existing = {ex.name.lower(): ex for ex in graph.nodes_of_type(Example)}
        for entry in entries:
            name = entry.get("export_name") or ""
            example = existing.get(name.lower())
            if example is None:
                owner = self._example_owner(graph, entry, epics, subs, stories)
                order = len(getattr(owner, "examples", []) or []) + 1 if owner is not None else 1
                if owner is not None and hasattr(owner, "load_example"):
                    example = owner.load_example(
                        Example(name, order, {}, scope=entry.get("owner_kind") or "story")
                    )
                else:
                    example = Example(name, order, {}, scope=entry.get("owner_kind") or "story")
                graph.register(example)
                existing[name.lower()] = example
                if owner is not None:
                    owner.examples.append(example)
                    owner.relate(Kind.SCOPES, example)


    def _wire_step_demonstrated_through(self, graph: PracticeGraph, created_steps) -> None:
        by_name: Dict[str, Example] = {}
        for example in graph.nodes_of_type(Example):
            by_name[example.name] = example
            by_name[example.name.lower()] = example
        for entry, step in created_steps:
            for name in entry.get("uses_examples") or []:
                example = by_name.get(name) or by_name.get(name.lower())
                if example is None:
                    continue
                step.relate(Kind.DEMONSTRATED_THROUGH, example)


    def _example_owner(self, graph, entry, epics, subs, stories):
        kind = entry.get("owner_kind") or ""
        owner = entry.get("owner") or ""
        if kind == "story_map":
            return graph.story_map
        if kind == "epic":
            return epics.get(Node.slug(owner))
        if kind == "sub_epic":
            for (_epic, sub_slug), sub in subs.items():
                if sub_slug == Node.slug(owner):
                    return sub
            return None
        if kind == "story":
            return stories.get(Node.slug(owner))
        owner_slug = Node.slug(owner) if owner else ""
        if owner_slug in epics:
            return epics[owner_slug]
        for (_epic, sub_slug), sub in subs.items():
            if sub_slug == owner_slug:
                return sub
        if not owner_slug:
            return graph.story_map
        return None


    def _step_owner(self, scenarios, backgrounds, entry):
        if entry.get("scenario"):
            key = (
                self._norm_file(entry.get("file") or ""),
                Node.slug(entry.get("story") or ""),
                (entry.get("scenario") or "").lower(),
            )
            found = scenarios.get(key)
            if found is not None:
                return found
            for (file_key, story_slug, scenario_name), scenario in scenarios.items():
                if scenario_name == (entry.get("scenario") or "").lower() and story_slug == Node.slug(entry.get("story") or ""):
                    return scenario
        if entry.get("background"):
            for bg_entry, background in backgrounds:
                if Node.slug(bg_entry.get("story") or "") != Node.slug(entry.get("story") or ""):
                    continue
                if (bg_entry.get("name") or "background") == (entry.get("background") or "background"):
                    return background
        return None


    def _phase_for(self, phase: str, keyword: str) -> Phase:
        value = (phase or keyword or "given").lower()
        mapping = {"given": Phase.GIVEN, "when": Phase.WHEN, "then": Phase.THEN}
        if value in {"and", "but"}:
            return Phase.THEN
        return mapping.get(value, Phase.GIVEN)


    def _display(self, name: str) -> str:
        if not name:
            return ""
        if " " in name:
            return name
        return name.replace("-", " ").replace("_", " ").title()


    def _norm_file(self, path: str) -> str:
        return path.replace("\\", "/").lstrip("./")


    def _attach_parameters(self, graph: PracticeGraph, classes: Dict[str, OoadClass], rows: List[dict]) -> None:
        for row in rows:
            cls = classes.get((row.get("class_name") or "").lower())
            if cls is None:
                continue
            op = next((o for o in cls.operation_nodes if o.name == row.get("operation")), None)
            if op is None:
                continue
            name = row.get("name") or ""
            if not name or any(p.name == name for p in op.parameters):
                continue
            param = op.load_parameter(SourceParameter(name, len(op.parameters) + 1))
            op.parameters.append(param)
            graph.register(param)
            op.relate(Kind.HAS_PARAMETER, param)
            param.relate(Kind.BELONGS_TO, op)


    def _home_module(self, graph: PracticeGraph, cls) -> Optional[Module]:
        if cls is None:
            return None
        for node in cls.related(Kind.OWNS, direction="in"):
            if isinstance(node, Module):
                return node
        return None


    def _calls_within_depth(self, rows: List[dict], limit: int) -> List[dict]:
        del limit
        seen: set[tuple] = set()
        out: List[dict] = []
        for row in rows:
            key = (
                row.get("caller_class"),
                row.get("caller_operation"),
                row.get("callee_class"),
                row.get("callee_operation"),
            )
            if key in seen:
                continue
            seen.add(key)
            out.append(row)
        return out


    def _wire_calls(self, graph: PracticeGraph, calls: List[dict]) -> None:
        for call in calls:
            caller = graph.operation_named( call.get("caller_class") or "", call.get("caller_operation") or ""
            )
            callee = graph.operation_named( call.get("callee_class") or "", call.get("callee_operation") or ""
            )
            if caller is None or callee is None:
                continue
            caller.relate(Kind.INVOKES, callee)
            caller_cls = graph.class_named( call.get("caller_class") or "")
            callee_cls = graph.class_named( call.get("callee_class") or "")
            if caller_cls is not None and callee_cls is not None and caller_cls is not callee_cls:
                caller_cls.relate(Kind.DEPENDS_ON, callee_cls)
            caller_mod = self._home_module(graph, caller_cls)
            callee_mod = self._home_module(graph, callee_cls)
            if caller_mod is None or callee_mod is None or caller_mod is callee_mod:
                continue
            caller_mod.relate(Kind.DEPENDS_ON, callee_mod)
            if callee_mod.name not in caller_mod.dependencies:
                caller_mod.dependencies.append(callee_mod.name)


    def _wire_story_calls(self, graph: PracticeGraph, story_calls: List[dict]) -> None:
        for story_call in story_calls:
            step = self._find_step(
                graph,
                story_call.get("story_file") or "",
                int(story_call.get("line") or 0),
                story_call.get("step_text") or "",
            )
            operation = graph.operation_named(
                story_call.get("callee_class") or "",
                story_call.get("callee_operation") or "",
            )
            if step is None or operation is None:
                continue
            step.relate(Kind.INVOKES, operation)


    def _wire_story_observations(self, graph: PracticeGraph, observations: List[dict]) -> None:
        for obs in observations:
            step = self._find_step(graph, obs.get("story_file") or "", int(obs.get("line") or 0), "")
            if step is None:
                continue
            cls = graph.class_named( obs.get("target_class") or "")
            if cls is None:
                continue
            target = None
            for owned in cls.related(Kind.OWNS):
                if obs.get("member_kind") == "operation" and isinstance(owned, Operation):
                    if owned.name == obs.get("target_member"):
                        target = owned
                        break
                if obs.get("member_kind") == "property" and isinstance(owned, Property):
                    if owned.name == obs.get("target_member"):
                        target = owned
                        break
            if target is not None:
                step.relate(Kind.OBSERVES, target)


    def _wire_example_demonstrates(self, graph: PracticeGraph, entries: List[dict]) -> None:
        examples_by_name: Dict[str, List[Example]] = {}
        for example in graph.nodes_of_type(Example):
            examples_by_name.setdefault(example.name.lower(), []).append(example)

        for entry in entries:
            cls_names = entry.get("demonstrates") or []
            if not cls_names:
                continue
            matched = self._match_examples(examples_by_name, entry.get("export_name") or "", entry.get("file") or "")
            for example in matched:
                for class_name in cls_names:
                    cls = graph.class_named( class_name)
                    if cls is not None:
                        example.relate(Kind.DEMONSTRATES, cls)


    def _match_examples(self, 
        index: Dict[str, List[Example]],
        export_name: str,
        file_path: str,
    ) -> List[Example]:
        export_lower = export_name.lower()
        if export_lower in index:
            return index[export_lower]
        stem = Path(file_path).stem.replace(".examples", "").replace("-", " ")
        if stem.lower() in index:
            return index[stem.lower()]
        out: List[Example] = []
        for examples in index.values():
            for ex in examples:
                if export_lower in ex.name.lower() or ex.name.lower() in export_lower:
                    out.append(ex)
        return out


    def _find_step(self, 
        graph: PracticeGraph,
        story_file: str,
        line: int,
        step_text: str,
    ) -> Optional[Step]:
        normalized = story_file.replace("\\", "/").lstrip("./")
        best: Tuple[int, Optional[Step]] = (1_000_000, None)
        for step in graph.nodes_of_type(Step):
            if step_text and step_text.lower() in step.text.lower():
                return step
            src = getattr(step, "source", None)
            if src is None:
                continue
            src_file = str(src.file).replace("\\", "/").lstrip("./")
            if src_file != normalized and not src_file.endswith(normalized):
                continue
            if line <= 0:
                return step
            delta = abs(int(src.line) - line)
            if delta < best[0]:
                best = (delta, step)
        if best[1] is not None and best[0] <= 5:
            return best[1]
        return None
