"""CodeQL collaborator — database, queries, and graph populate."""

from __future__ import annotations

import json
import os
import shutil
import signal
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

    def entity_name(self, item) -> str:
        raw = item.get("label", item) if isinstance(item, dict) else str(item)
        text = str(raw)
        for prefix in ("Class ", "Function ", "Module ", "File ", "Script "):
            if text.startswith(prefix):
                return text[len(prefix) :]
        return text

    def entity_location(self, item) -> tuple[str, int]:
        if not isinstance(item, dict):
            return "", 0
        url = item.get("url")
        if isinstance(url, dict):
            return self._file_from_uri(str(url.get("uri") or "")), int(
                url.get("startLine") or 0
            )
        if isinstance(url, str) and url:
            path, _, rest = url.partition(":")
            if path.startswith("file"):
                file, line = self._split_file_url(url)
                return file, line
            line = 0
            if rest:
                try:
                    line = int(rest.split(":")[0])
                except ValueError:
                    line = 0
            return self._file_from_uri(path), line
        return "", 0

    def _split_file_url(self, url: str) -> tuple[str, int]:
        stripped = url
        if stripped.startswith("file://"):
            stripped = stripped[7:]
            if stripped.startswith("/") and len(stripped) > 2 and stripped[2] == ":":
                stripped = stripped[1:]
        file_part, _, rest = stripped.partition(":")
        if len(file_part) == 1 and rest:
            drive, _, rest = rest.partition(":")
            file_part = f"{file_part}:{drive}"
        line = 0
        if rest:
            try:
                line = int(rest.split(":")[0])
            except ValueError:
                line = 0
        return file_part.replace("\\", "/"), line

    def _file_from_uri(self, uri: str) -> str:
        text = uri
        if text.startswith("file://"):
            text = text[7:]
            if text.startswith("/") and len(text) > 2 and text[2] == ":":
                text = text[1:]
        return text.split("?")[0].replace("\\", "/")

    def entity_kind(self, item) -> str:
        raw = item.get("label", item) if isinstance(item, dict) else str(item)
        text = str(raw)
        for prefix, kind in (
            ("Class ", "Class"),
            ("Function ", "Function"),
            ("Module ", "Module"),
            ("File ", "File"),
            ("Script ", "Module"),
        ):
            if text.startswith(prefix):
                return kind
        return ""

    @classmethod
    def from_tuples(cls, tuples: List[list]) -> "Rows":
        decoder = cls()
        return cls([decoder._row_from_tuple(item) for item in tuples if item])

    def _row_from_tuple(self, item: list) -> dict:
        message = item[1] if len(item) > 1 else ""
        if isinstance(message, dict):
            message = message.get("label", "")
        file, line = self.entity_location(item[0])
        row = {"name": self.entity_name(item[0]), "message": str(message)}
        kind = self.entity_kind(item[0])
        if kind:
            row["kind"] = kind
        if file:
            row["file"] = file
        if line:
            row["line"] = line
        if len(item) > 2:
            contributor = self.entity_name(item[2])
            if contributor:
                row["contributor"] = contributor
        return row

class CodeQL:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._pending_batch = {}
        self._pending_results = None
        self._database_language = "python"

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
        working = self.root / ".codeql" / f"{language}-working-copy"
        ready = self._ready_database(language)
        if ready is not None:
            return ready
        self._retire_database(working)
        self._database_language = language
        return self._create_database(working)

    @property
    def master(self) -> Path:
        return self.root / ".codeql" / "python-master"

    @property
    def working_copy(self) -> Path:
        return self.root / ".codeql" / "python-working-copy"

    def rewrite_master(self, language: str = "python") -> Path:
        self._unlock_databases()
        database = self.root / ".codeql" / f"{language}-master"
        building = database.with_name(f"{language}-master.building")
        self._retire_database(building)
        self._database_language = language
        created = self._create_database(building)
        return self._install_created_database(created, database)

    def extract_working_copy(self, paths: list[Path]) -> Path:
        if not paths:
            return self.working_copy
        return self.rewrite_working_copy()

    def _create_database(self, database: Path) -> Path:
        language = getattr(self, "_database_language", "python")
        source_root = self.root
        database.parent.mkdir(parents=True, exist_ok=True)
        run = subprocess.run(
            [
                self.executable(),
                "database",
                "create",
                str(database),
                f"--language={language}",
                f"--source-root={source_root}",
                "--build-mode=none",
                "--overwrite",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if run.returncode != 0 or not self._database_ready(database):
            raise self._failed_codeql(run)
        return database

    def _failed_codeql(self, run) -> CodeQLRunError:
        detail = "\n".join(part for part in (run.stderr, run.stdout) if part)
        return CodeQLRunError(f"codeql failed: {detail}")

    def copy_master_to_working_copy(self) -> Path:
        self._unlock_databases()
        self._copy_database(self.master, self.working_copy)
        return self.working_copy

    def rewrite_working_copy(self) -> Path:
        self._unlock_databases()
        database = self.working_copy
        building = database.with_name("python-working-copy.building")
        self._retire_database(building)
        self._database_language = "python"
        created = self._create_database(building)
        return self._install_created_database(created, database)

    def copy_working_copy_to_master(self) -> Path:
        self._unlock_databases()
        self._copy_database(self.working_copy, self.master)
        return self.master

    def _install_created_database(self, created: Path, database: Path) -> Path:
        self._retire_database(database)
        try:
            created.rename(database)
            return database
        except OSError:
            return self._copy_created_database(created, database)

    def _copy_created_database(self, created: Path, database: Path) -> Path:
        self._copy_database(created, database)
        shutil.rmtree(created, ignore_errors=True)
        if not self._database_ready(database):
            raise CodeQLRunError(f"could not install database at {database}")
        return database

    def _copy_database(self, source: Path, destination: Path) -> None:
        self._retire_database(destination)
        if destination.is_file() or destination.is_symlink():
            destination.unlink()
        if destination.exists():
            shutil.copytree(source, destination, dirs_exist_ok=True)
            return
        shutil.copytree(source, destination)

    def _unlock_databases(self) -> None:
        detach_query_server()
        path = self.repo_root() / ".codeql" / "query-server.json"
        if not path.is_file():
            return
        try:
            pid = int(json.loads(path.read_text(encoding="utf-8")).get("pid") or 0)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            return
        if pid in (0, os.getpid()):
            return
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError:
            return
        time.sleep(0.5)

    def _retire_database(self, database: Path) -> None:
        if not database.exists():
            return
        retired = database.with_name(database.name + ".retired")
        for _ in range(6):
            if retired.exists():
                shutil.rmtree(retired, ignore_errors=True)
            try:
                database.rename(retired)
                shutil.rmtree(retired, ignore_errors=True)
            except OSError:
                shutil.rmtree(database, ignore_errors=True)
            if not database.exists():
                return
            time.sleep(0.4)

    def class_rows(self, tuples: List[list] | None = None) -> Rows:
        if tuples is None:
            tuples = self.run_query_tuples(
                _CODEQL_QUERIES / "classes.ql", self.ensure_database("python")
            )
        return Rows(
            {
                "name": self._cell(row, 0),
                "module": self._cell(row, 1),
                "file": self._cell(row, 2),
                "line": self._int_cell(row, 3),
                "end_line": self._int_cell(row, 4),
            }
            for row in tuples
            if self._cell(row, 0)
        )

    def operation_rows(self, tuples: List[list] | None = None) -> Rows:
        if tuples is None:
            tuples = self.run_query_tuples(
                _CODEQL_QUERIES / "operations.ql", self.ensure_database("python")
            )
        return Rows(
            {
                "class_name": self._cell(row, 0),
                "name": self._cell(row, 1),
                "return_type": self._cell(row, 2),
                "line": self._int_cell(row, 3),
                "file": self._cell(row, 4),
                "end_line": self._int_cell(row, 5),
            }
            for row in tuples
            if self._cell(row, 0) and self._cell(row, 1)
        )

    def parameter_rows(self, tuples: List[list] | None = None) -> Rows:
        if tuples is None:
            tuples = self.run_query_tuples(
                _CODEQL_QUERIES / "parameters.ql", self.ensure_database("python")
            )
        return Rows(
            {
                "class_name": self._cell(row, 0),
                "operation": self._cell(row, 1),
                "name": self._cell(row, 2),
                "line": self._int_cell(row, 3),
                "file": self._cell(row, 4),
                "end_line": self._int_cell(row, 5),
            }
            for row in tuples
            if self._cell(row, 0) and self._cell(row, 1) and self._cell(row, 2)
        )

    def property_rows(self, tuples: List[list] | None = None) -> Rows:
        if tuples is None:
            tuples = self.run_query_tuples(
                _CODEQL_QUERIES / "properties.ql", self.ensure_database("python")
            )
        return Rows(
            {
                "class_name": self._cell(row, 0),
                "name": self._cell(row, 1),
                "module": self._cell(row, 2),
                "line": self._int_cell(row, 3),
                "file": self._cell(row, 4),
                "end_line": self._int_cell(row, 5),
            }
            for row in tuples
            if self._cell(row, 0) and self._cell(row, 1)
        )

    def call_rows(self, tuples: List[list] | None = None) -> Rows:
        if tuples is None:
            tuples = self.run_query_tuples(
                _CODEQL_QUERIES / "calls.ql", self.ensure_database("python")
            )
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
        for candidate in (
            self.working_copy / "practice-graph.json",
            self.master / "practice-graph.json",
        ):
            if candidate.is_file():
                return candidate
        return None

    def run(self, query: Path, database: Path | None = None) -> Rows:
        db = database if database is not None else self.ensure_database(self.query_language(query))
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
            self.query_language(queries[0])
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
            raise self._failed_codeql(run)
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
            raise self._failed_codeql(run)
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
        self.write_rules_query(query.parent)
        tuples = self.run_queries([query], database, write_filter=write_filter).get(query.stem) or []
        return self._rows_by_slug(tuples, slugs)

    def write_rules_query(self, pack_dir: Path) -> None:
        language = self.pack_language(pack_dir) or "python"
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
            raise self._failed_codeql(decode)
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
        for context in self.root.rglob("module-context.md"):
            prefix = self._module_prefix_from_context(context, path_root)
            if prefix and prefix not in prefixes:
                prefixes.append(prefix)
        return self._without_catalog_prefixes(prefixes, path_root)

    def _without_catalog_prefixes(
        self, prefixes: List[str], path_root: Path
    ) -> List[str]:
        catalogs = {
            prefix
            for prefix in prefixes
            if self._is_catalog_prefix(prefix, prefixes, path_root)
        }
        promoted = list(prefixes)
        for catalog in catalogs:
            for child in self._child_package_prefixes(path_root / catalog, catalog):
                if child not in promoted:
                    promoted.append(child)
        return [prefix for prefix in promoted if prefix not in catalogs]

    def _is_catalog_prefix(
        self, prefix: str, prefixes: List[str], path_root: Path
    ) -> bool:
        nested = any(
            other.startswith(f"{prefix}/") for other in prefixes if other != prefix
        )
        if not nested:
            return False
        folder = path_root / prefix
        if not folder.is_dir():
            return True
        return not any(self._is_own_python_file(child) for child in folder.iterdir())

    def _is_own_python_file(self, path: Path) -> bool:
        return (
            path.is_file()
            and path.suffix == ".py"
            and path.name != "__init__.py"
            and not path.name.endswith("_spec.py")
            and not path.name.startswith("test_")
        )

    def _child_package_prefixes(self, folder: Path, prefix: str) -> List[str]:
        skip = {"examples", "node_modules", ".git", "__pycache__", ".venv", "venv"}
        if not folder.is_dir():
            return []
        children: List[str] = []
        for child in sorted(folder.iterdir()):
            if not child.is_dir() or child.name in skip or child.name.startswith("."):
                continue
            if not any(self._is_own_python_file(path) for path in child.iterdir()):
                continue
            children.append(f"{prefix}/{child.name}")
        return children

    def _module_prefix_from_context(self, context: Path, path_root: Path) -> str:
        skip = {"examples", "node_modules", ".git", "__pycache__", ".venv", "venv"}
        if context.parent.name != ".context" or not context.is_file():
            return ""
        try:
            relative = context.resolve().relative_to(self.root.resolve())
        except ValueError:
            return ""
        if any(part in skip for part in relative.parts):
            return ""
        folder = context.parent.parent
        try:
            prefix = folder.resolve().relative_to(path_root.resolve()).as_posix()
        except ValueError:
            return ""
        if prefix in (".", ""):
            return ""
        return prefix

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
        if name.endswith("_spec.py") or name.startswith("test_"):
            return True
        if "/examples/" not in f"/{path}":
            return False
        root = self.root.resolve().as_posix().replace("\\", "/").lower()
        return root not in path.lower()

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
            path_body = "  any()\n"
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
        binding = "bindingset[path]\n"
        text = (
            f"import {language}\n\n"
            f'predicate subjectFilterPrefix(string prefix) {{ prefix = "{prefix}" }}\n\n'
            f"{self._ql_prefix_predicate('firstClassModulePrefix', modules)}\n"
            f"predicate inSubject({ast} n) {{\n"
            '  inSubjectPath(n.getLocation().getFile().getRelativePath().replaceAll("\\\\", "/"))\n'
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

    def pack_language(self, pack_dir: Path) -> str | None:
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

    def query_language(self, ql_path: Path) -> str:
        return self.pack_language(ql_path.parent) or self._file_language(ql_path)

    def query_matches_pack(self, ql_path: Path) -> bool:
        pack_language = self.pack_language(ql_path.parent)
        if pack_language is None:
            return True
        return pack_language == self._file_language(ql_path)

    def _database_ready(self, database: Path) -> bool:
        has_db = (database / "db-python").is_dir() or (database / "db-javascript").is_dir()
        return has_db and (database / "codeql-database.yml").is_file()

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
        database: Path | None = None,
        *,
        results_path: str | Path | None = None,
        populate: bool = True,
    ) -> None:
        self._pending_results = results_path
        if not populate and self._load_cached_facts(graph):
            return
        db = database if database is not None else self.ensure_database("python")
        self._write_subject_filter(_CODEQL_QUERIES, path_root=self._ql_path_root(db))
        populate_queries = self._populate_query_paths()
        print(f"run-queries populate ({len(populate_queries)} queries) ...", flush=True)
        started = time.perf_counter()
        batch = self.run_queries(populate_queries, db)
        seconds = time.perf_counter() - started
        from .practice_graph import RuleTiming

        graph.record_rule_timing(
            RuleTiming("run-queries:knowledge-graph", seconds, len(batch.get("classes") or []))
        )
        print(f"run-queries populate  {seconds:.2f}s", flush=True)
        self._pending_batch = batch
        self._apply_fact_batch(graph)

    def _populate_query_paths(self) -> List[Path]:
        return [
            _CODEQL_QUERIES / "classes.ql",
            _CODEQL_QUERIES / "operations.ql",
            _CODEQL_QUERIES / "parameters.ql",
            _CODEQL_QUERIES / "properties.ql",
            _CODEQL_QUERIES / "calls.ql",
        ]

    def _ready_database(self, language: str = "python") -> Path | None:
        working = self.root / ".codeql" / f"{language}-working-copy"
        master = self.root / ".codeql" / f"{language}-master"
        if self._database_ready(working):
            return working
        if self._database_ready(master):
            return master
        return None

    def _load_cached_facts(self, graph: PracticeGraph) -> bool:
        try:
            self.load_existing_facts(graph, results_path=self._pending_results)
            return True
        except CodeQLRunError as error:
            graph.record_partial_failure("load cached facts", error)
        existing = self.results_path(
            Path(self._pending_results) if self._pending_results is not None else None
        )
        if existing is None:
            return False
        self._pending_batch = {
            "classes": [],
            "operations": [],
            "properties": [],
            "parameters": [],
            "calls": [],
        }
        self._pending_results = existing
        self._apply_fact_batch(graph)
        return True

    def load_existing_facts(
        self,
        graph: PracticeGraph,
        *,
        results_path: str | Path | None = None,
    ) -> None:
        database = self._ready_database("python")
        if database is None:
            raise CodeQLRunError(
                f"no python-master or python-working-copy under {self.root / '.codeql'}"
            )
        populate_queries = self._populate_query_paths()
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
        self._pending_batch = batch
        self._pending_results = results_path
        self._apply_fact_batch(graph)

    def _apply_fact_batch(self, graph: PracticeGraph) -> None:
        batch = self._pending_batch
        results_path = self._pending_results
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
        if not class_rows and not operation_rows and not (raw and (raw.get("stories") or raw.get("steps"))):
            raise RuntimeError(f"CodeQL returned no classes or stories for {self.root}")
        self._assign_module_names(class_rows)
        from practices.clean_engineering.model.codeql.codeql_model import (
            CleanEngineeringModel,
            GraphMemberRows,
        )
        from practices.stories.model.codeql.codeql_model import StoryMap

        model = CleanEngineeringModel("CleanEngineering", 1)
        rows = GraphMemberRows(class_rows, property_rows)
        rows.operations = operation_rows
        rows.parameters = parameter_rows
        model.ensure(
            graph,
            rows,
        )
        model.wire_calls(graph, call_rows)
        if raw:
            StoryMap().ensure(graph, raw)

    def _optional_json(self, results_path) -> Optional[dict]:
        path = self.results_path(Path(results_path) if results_path else None)
        if path is None:
            return None
        return json.loads(path.read_text(encoding="utf-8"))

