"""CodeQL collaborator — database, queries, and graph populate."""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from .practice_graph import PracticeGraph

_CODEQL_QUERIES = (
    Path(__file__).resolve().parents[3]
    / "practices"
    / "clean_engineering"
    / "model"
    / "codeql"
)
_RUN_QUERIES_FLAGS = ("--threads=0", "--quiet")


class CodeQLRunError(RuntimeError):
    """CodeQL CLI was missing, the database was missing, or the query failed."""


class QueryServerDown(CodeQLRunError):
    """The long-lived query server process is gone or its stream closed."""


_attached_query_server = None


def attach_query_server(server) -> None:
    """Keep the MCP host's CodeQL process as the runner for later batches."""
    global _attached_query_server
    _attached_query_server = server


def detach_query_server(server=None) -> None:
    global _attached_query_server
    if server is None or _attached_query_server is server:
        _attached_query_server = None


def attached_query_server():
    return _attached_query_server


class Rows(list):
    """Decoded CodeQL select tuples as dict rows."""

    @staticmethod
    def entity_name(item) -> str:
        raw = item.get("label", item) if isinstance(item, dict) else str(item)
        text = str(raw)
        for prefix in ("Class ", "Function ", "Module ", "File ", "Script "):
            if text.startswith(prefix):
                return text[len(prefix) :]
        return text

    @classmethod
    def from_tuples(cls, tuples: List[list]) -> "Rows":
        rows: List[dict] = []
        for item in tuples:
            if not item:
                continue
            message = item[1] if len(item) > 1 else ""
            if isinstance(message, dict):
                message = message.get("label", "")
            row = {"name": cls.entity_name(item[0]), "message": str(message)}
            if len(item) > 2:
                contributor = cls.entity_name(item[2])
                if contributor:
                    row["contributor"] = contributor
            rows.append(row)
        return cls(rows)


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
        db = database if database is not None else self.ensure_database(self._query_language(query))
        self._write_subject_filter(query.parent, path_root=self._ql_path_root(db))
        return Rows.from_tuples(self.run_query_tuples(query, db))

    def run_queries(
        self,
        queries: List[Path],
        database: Path | None = None,
        *,
        write_filter: bool = True,
    ) -> Dict[str, List[list]]:
        if not queries:
            return {}
        db = database if database is not None else self.ensure_database(
            self._query_language(queries[0])
        )
        if write_filter:
            self._write_subject_filter(queries[0].parent, path_root=self._ql_path_root(db))
        server = attached_query_server()
        if server is not None and getattr(server, "alive", False):
            self._emit("query-server " + " ".join(query.stem for query in queries))
            try:
                produced = server.run_queries(queries, db, self._emit)
                decoded: Dict[str, List[list]] = {}
                for query in queries:
                    key = str(query.resolve())
                    if key not in produced:
                        decoded[query.stem] = []
                        continue
                    decoded[query.stem] = self._decode_bqrs(produced[key])
                return decoded
            except QueryServerDown as error:
                self._emit(
                    f"query server failed ({error}); falling back to database run-queries"
                )
                self._restart_query_server(server)
            except CodeQLRunError:
                raise
            except Exception as error:
                self._emit(
                    f"query server failed ({error}); falling back to database run-queries"
                )
                self._restart_query_server(server)
        run = subprocess.run(
            self._run_queries_args(db, queries),
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

    def _produce_bqrs(self, queries, database):
        server = attached_query_server()
        if server is not None and getattr(server, "alive", False):
            return server.run_queries(queries, database, self._emit)
        run = subprocess.run(
            self._run_queries_args(database, queries),
            check=False,
            capture_output=True,
            text=True,
            cwd=str(self.repo_root()),
        )
        if run.returncode != 0:
            raise CodeQLRunError(
                f"codeql database run-queries failed: {run.stderr or run.stdout}"
            )
        return {
            str(query.resolve()): self._bqrs_for(database, query) for query in queries
        }

    def _emit(self, line: str) -> None:
        print(line, flush=True)

    def _restart_query_server(self, server) -> None:
        try:
            server.stop()
            server.start()
        except Exception as error:
            self._emit(f"query server restart failed ({error})")
            detach_query_server(server)

    def run_query_tuples(self, ql_path: Path, database: Path) -> List[list]:
        return self.run_queries([ql_path], database)[ql_path.stem]

    def run_rules(
        self,
        query: Path,
        slugs: List[str],
        database: Path | None = None,
        *,
        write_filter: bool = True,
    ) -> Dict[str, List[list]]:
        self._write_requested_rules(query.parent, slugs)
        self._write_rules_query(query.parent)
        tuples = self.run_queries([query], database, write_filter=write_filter).get(query.stem) or []
        return self._rows_by_slug(tuples, slugs)

    def _write_rules_query(self, pack_dir: Path) -> None:
        language = self._pack_language(pack_dir) or "python"
        text = (
            "/**\n"
            " * @name practice-graph-rules\n"
            " * @kind problem\n"
            " * @id cdd/practice-graph/rules\n"
            " * @problem.severity warning\n"
            " *\n"
            " * One query for every graph rule in this pack. `requestedRule` selects\n"
            " * which slugs this pass evaluates; each row still names its rule.\n"
            " */\n"
            "\n"
            f"import {language}\n"
            "import subject_filter\n"
            "import requested_rules\n"
            "import rule_hits\n"
            "\n"
            "from AstNode subject, string message, AstNode contributor, string slug\n"
            "where\n"
            "  requestedRule(slug) and\n"
            "  graphRuleHit(subject, message, contributor, slug)\n"
            "select subject, message, contributor, slug\n"
        )
        target = pack_dir / "rules.ql"
        if target.is_file() and target.read_text(encoding="utf-8") == text:
            return
        target.write_text(text, encoding="utf-8")

    def _rows_by_slug(self, tuples: List[list], slugs: List[str]) -> Dict[str, List[list]]:
        grouped: Dict[str, List[list]] = {slug: [] for slug in slugs}
        for row in tuples:
            slug = self._cell(row, 3)
            grouped.setdefault(slug, []).append(row[:3] if len(row) > 3 else row)
        return grouped

    def _write_requested_rules(self, pack_dir: Path, slugs: List[str]) -> None:
        if not slugs:
            body = "predicate requestedRule(string slug) { none() }\n"
        else:
            clauses = " or\n  ".join(f'slug = "{item}"' for item in slugs)
            body = f"predicate requestedRule(string slug) {{\n  {clauses}\n}}\n"
        text = (
            "/** Which graph-query rule slugs this pass evaluates. CodeQL overwrites this file. */\n\n"
            + body
        )
        target = pack_dir / "requested_rules.qll"
        if target.is_file() and target.read_text(encoding="utf-8") == text:
            return
        target.write_text(text, encoding="utf-8")


    def _run_queries_args(self, database: Path, queries: List[Path]) -> List[str]:
        return [
            self.executable(),
            "database",
            "run-queries",
            *_RUN_QUERIES_FLAGS,
            str(database),
            "--",
            *[str(query.resolve()) for query in queries],
        ]

    def _pack_results_dir(self, query: Path) -> Path:
        name = "cdd/clean-engineering-graph-query"
        qlpack = query.parent / "qlpack.yml"
        if qlpack.is_file():
            for line in qlpack.read_text(encoding="utf-8").splitlines():
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                    break
        return Path(*name.split("/"))

    def _bqrs_for(self, database: Path, query: Path) -> Path:
        results = database / "results"
        direct = results / self._pack_results_dir(query) / f"{query.stem}.bqrs"
        if direct.is_file():
            return direct
        matches = list(results.rglob(f"{query.stem}.bqrs")) if results.is_dir() else []
        if not matches:
            raise CodeQLRunError(f"no bqrs for {query.stem} under {results}")
        return max(matches, key=lambda p: p.stat().st_mtime)

    def _decode_bqrs(self, bqrs: Path) -> List[list]:
        decode = subprocess.run(
            [self.executable(), "bqrs", "decode", str(bqrs), "--format=json"],
            check=False,
            capture_output=True,
            text=True,
        )
        if decode.returncode != 0 or not decode.stdout.strip():
            raise CodeQLRunError(
                f"codeql bqrs decode failed for {bqrs}: {decode.stderr or decode.stdout}"
            )
        payload = json.loads(decode.stdout)
        return payload.get("#select", {}).get("tuples", [])

    def _ql_path_root(self, database: Path) -> Path:
        if database.parent.name == ".codeql":
            return database.parent.parent.resolve()
        return self.repo_root()

    def _subject_prefix(self, path_root: Path) -> str:
        try:
            prefix = self.root.resolve().relative_to(path_root.resolve()).as_posix().rstrip("/")
        except ValueError:
            return ""
        if prefix in ("", "."):
            return ""
        return prefix

    def _first_class_module_prefixes(self, path_root: Path) -> List[str]:
        prefixes: List[str] = []
        subject = self._subject_prefix(path_root)
        if subject:
            prefixes.append(subject)
        skip = {"examples", "node_modules", ".git", "__pycache__", ".venv", "venv"}
        for context in self.root.rglob("module-context.md"):
            if context.parent.name != ".context" or not context.is_file():
                continue
            try:
                relative = context.resolve().relative_to(self.root.resolve())
            except ValueError:
                continue
            if any(part in skip for part in relative.parts):
                continue
            folder = context.parent.parent
            try:
                prefix = folder.resolve().relative_to(path_root.resolve()).as_posix()
            except ValueError:
                continue
            if prefix and prefix not in prefixes:
                prefixes.append(prefix)
        return prefixes

    def _owning_module_prefix(self, file_path: str, prefixes: List[str]) -> str:
        path = str(file_path or "").replace("\\", "/").lstrip("./")
        matches = [
            prefix
            for prefix in prefixes
            if prefix and (path == prefix or path.startswith(prefix + "/"))
        ]
        if matches:
            return max(matches, key=len)
        return prefixes[0] if prefixes else ""

    def _skipped_graph_path(self, file_path: str) -> bool:
        path = str(file_path or "").replace("\\", "/")
        name = Path(path).name
        return (
            "/examples/" in f"/{path}"
            or name.endswith("_spec.py")
            or name.startswith("test_")
        )

    def _ql_prefix_predicate(self, name: str, prefixes: List[str]) -> str:
        if not prefixes:
            return f"predicate {name}(string prefix) {{ none() }}\n"
        clauses = " or\n  ".join(f'prefix = "{item}"' for item in prefixes)
        return f"predicate {name}(string prefix) {{\n  {clauses}\n}}\n"

    def _write_subject_filter(self, pack_dir: Path, path_root: Path | None = None) -> None:
        root = (path_root or self.repo_root()).resolve()
        prefix = self._subject_prefix(root)
        modules = self._first_class_module_prefixes(root)
        if prefix:
            path_body = (
                "  exists(string filterPrefix, string normalized |\n"
                "    subjectFilterPrefix(filterPrefix) and\n"
                '    normalized = path.replaceAll("\\\\", "/") and\n'
                "    (normalized = filterPrefix or normalized.matches(filterPrefix + \"/%\"))\n"
                "  )\n"
            )
        else:
            path_body = (
                "  exists(File f |\n"
                '    path = f.getRelativePath().replaceAll("\\\\", "/")\n'
                "  )\n"
            )
        language = "python"
        qlpack = pack_dir / "qlpack.yml"
        if qlpack.is_file() and "javascript" in qlpack.read_text(encoding="utf-8"):
            language = "javascript"
        ast = "AstNode"
        extra = ""
        if language == "python":
            extra = (
                "\npredicate inSubjectFilter(Class cls) {\n"
                "  inSubject(cls)\n"
                "}\n"
            )
        binding = "bindingset[path]\n" if prefix else ""
        text = (
            f"import {language}\n\n"
            f'predicate subjectFilterPrefix(string prefix) {{ prefix = "{prefix}" }}\n\n'
            f"{self._ql_prefix_predicate('firstClassModulePrefix', modules)}\n"
            f"predicate inSubject({ast} n) {{\n"
            "  inSubjectPath(n.getLocation().getFile().getRelativePath())\n"
            "}\n"
            f"{extra}\n"
            f"{binding}predicate inSubjectPath(string path) {{\n"
            f"{path_body}"
            "}\n"
        )
        target = pack_dir / "subject_filter.qll"
        if target.is_file() and target.read_text(encoding="utf-8") == text:
            return
        target.write_text(text, encoding="utf-8")

    def _pack_language(self, pack_dir: Path) -> str | None:
        qlpack = pack_dir / "qlpack.yml"
        if not qlpack.is_file():
            return None
        text = qlpack.read_text(encoding="utf-8")
        if "javascript-all" in text or "codeql/javascript" in text:
            return "javascript"
        if "python-all" in text or "codeql/python" in text:
            return "python"
        return None

    def _file_language(self, ql_path: Path) -> str:
        text = ql_path.read_text(encoding="utf-8")
        if "import javascript" in text:
            return "javascript"
        return "python"

    def _query_language(self, ql_path: Path) -> str:
        return self._pack_language(ql_path.parent) or self._file_language(ql_path)

    def _query_matches_pack(self, ql_path: Path) -> bool:
        pack_language = self._pack_language(ql_path.parent)
        if pack_language is None:
            return True
        return pack_language == self._file_language(ql_path)

    def _database_ready(self, database: Path) -> bool:
        return (database / "db-python").is_dir() or (database / "db-javascript").is_dir()

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

    def _assign_module_names(self, class_rows: List[dict]) -> None:
        prefixes = self._first_class_module_prefixes(self.repo_root())
        kept: List[dict] = []
        for entry in class_rows:
            file_path = entry.get("file") or ""
            if self._skipped_graph_path(file_path):
                continue
            owning = self._owning_module_prefix(file_path, prefixes)
            module_name = owning.replace("/", ".") if owning else (entry.get("module") or "")
            if not module_name:
                continue
            entry["module"] = module_name
            kept.append(entry)
        class_rows[:] = kept

    def populate(
        self,
        graph: PracticeGraph,
        *,
        results_path: str | Path | None = None,
        populate: bool = True,
    ) -> None:
        if not populate:
            self.load_existing_facts(graph, results_path=results_path)
            return
        database = self.ensure_database("python")
        self._write_subject_filter(_CODEQL_QUERIES, path_root=self._ql_path_root(database))
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
        from .practice_graph import RuleTiming

        graph.record_rule_timing(
            RuleTiming("run-queries:knowledge-graph", seconds, len(batch.get("classes") or []))
        )
        print(f"run-queries populate  {seconds:.2f}s", flush=True)
        self._apply_fact_batch(graph, batch, results_path)

    def load_existing_facts(
        self,
        graph: PracticeGraph,
        *,
        results_path: str | Path | None = None,
    ) -> None:
        database = self.ensure_database("python")
        populate_queries = [
            _CODEQL_QUERIES / "classes.ql",
            _CODEQL_QUERIES / "operations.ql",
            _CODEQL_QUERIES / "parameters.ql",
            _CODEQL_QUERIES / "properties.ql",
            _CODEQL_QUERIES / "calls.ql",
        ]
        started = time.perf_counter()
        batch = {
            query.stem: self._decode_bqrs(self._bqrs_for(database, query))
            for query in populate_queries
        }
        seconds = time.perf_counter() - started
        from .practice_graph import RuleTiming

        graph.record_rule_timing(
            RuleTiming("decode-facts:knowledge-graph", seconds, len(batch.get("classes") or []))
        )
        print(f"decode existing facts  {seconds:.2f}s", flush=True)
        self._apply_fact_batch(graph, batch, results_path)

    def _apply_fact_batch(
        self,
        graph: PracticeGraph,
        batch: Dict[str, List[list]],
        results_path: str | Path | None,
    ) -> None:
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
        self._assign_module_names(class_rows)
        from practices.clean_engineering.model.codeql.codeql_model import (
            CleanEngineeringModel,
        )
        from practices.stories.model.codeql.codeql_model import StoryMap

        CleanEngineeringModel.ensure(graph, class_rows, property_rows, operation_rows, parameter_rows)
        CleanEngineeringModel.wire_calls(graph, call_rows)
        if raw:
            StoryMap.ensure(graph, raw)

    def _optional_json(self, results_path) -> Optional[dict]:
        path = self.results_path(Path(results_path) if results_path else None)
        if path is None:
            return None
        return json.loads(path.read_text(encoding="utf-8"))

