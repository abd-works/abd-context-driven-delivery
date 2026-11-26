"""Infrastructure spec: the cdd server keeps answering every chat while chats' graph builds run.

A graph build is minutes of CPU-bound Python. Run in the server's own interpreter, it slowed the event loop until the
server stopped accepting connections and every chat lost its cdd tools. This spec starts a server of its own, on a port
of its own, in two ways chats build at once.

- Five chats, each on a project of its own, build every practice's graph of ``cdd_guidance/practices`` at once; each
  asks to hear its build's progress as Claude Code does.
- Six chats on one project refresh the one graph that project's session holds, each with files of its own, several
  times over: every practice is loaded in it first, so each refresh restores and refreshes a graph that holds every
  practice.
- Six chats on one project validate files of their own with ``validate.validate`` and ``graph: true``, as agents do:
  each validate refreshes the session's graph and checks the nodes of its files, which the graph's worker writes.

Meanwhile a crowd of other chats, as the Session Board's open pages are, keep asking a small graph tool, and one more
chat calls ``cdd.ping`` and that tool every half second for as long as any build runs, timing every answer.

Last, the Graph app's whole load (``graph.load_practice_roots``) of a session whose Stories, DDD and Clean Engineering
roots are three different folders, with a second folder added to DDD's tactics, holds the nodes a load of the same files
(``graph.load_files``) holds.

The four run at the same time, each on a server and a project of its own (``AllAtOnce``), and each context reads the
run it checks: the refreshes and the validates each take minutes of builds one after another, so running them in turn
doubled the file's time, and a machine busier with the other runs only makes each answer-time check harder to pass."""

import asyncio
import json
import shutil
import statistics
import sys
import tempfile
import threading
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import anyio
from expects import be_above, be_below, contain, equal, expect
from mamba import after, before, description, _it, it

from harness.mcp.spec_support import SpecServer

# The practices register with the catalogue when this toolset's module is imported, before the graph is made.
_TOOLSETS = ("cdd_guidance.practices.clean_engineering.clean_engineering:CleanEngineering", "harness.graph.graph:Graph")
# A validate works in the session its call's project holds, which the sessions' toolset registers with every call.
_VALIDATE_TOOLSETS = (*_TOOLSETS, "cdd_guidance.actions.validate.validate:Validate", "space.session.sessions:Sessions")
_VALIDATED_GUIDANCE = "clean-engineering-code"
_PRACTICE_KEYS = ("stories", "ddd", "ux", "clean_engineering", "bdd")
_PRACTICES = {key: "cdd_guidance/practices" for key in _PRACTICE_KEYS}
_PING_EVERY_SECONDS = 0.5
# How many chats build a graph at once, each on a project of its own.
_BUILDERS = 5
# How many other chats keep asking while the builds run, as the Session Board's pages do.
_CROWD = 20
_ANSWER_WITHIN_SECONDS = 2
_BUILD_SECONDS = 900
_LOADED = '{"message": "Loaded the working copies."}'
# The files each of the six validators refreshes in the shared graph, from the practices folder: code and specs, so
# every practice that reads the practices folder reads a file again.
_VALIDATED = (
    ("clean_engineering/model/operation.py", "clean_engineering/rules/class_rules.py"),
    ("stories/model/story_map.py", "stories/stories.py"),
    ("ddd/model/nodes.py", "ddd/reading/graph_reading.py"),
    ("bdd/model/graph_bdd_model_spec.py", "bdd/model/graph_reading.py"),
    ("ux/model/story_link.py", "ux/model/nodes.py"),
    ("clean_engineering/reading/graph_reading.py", "stories/model/graph_reading.py"),
)
# How many times each validator refreshes its files.
_ROUNDS = 2
# The Bookshop project the Stories specs read: a story map, story tests in markdown, Python and TypeScript, the DDD
# tactics code of the Order aggregate under ordering/, and the Clean Engineering code under src/. Copied as files only.
_BOOKSHOP = _REPO_ROOT / "cdd_guidance" / "practices" / "stories" / "model" / "fixtures" / "bookshop"
# The folder each practice of the session works in, and the second folder a person added to DDD's tactics.
_SESSION_ROOTS = {"stories": "story_tests", "ddd": "ordering", "clean_engineering": "src"}
_TACTICS_ROOTS = ["ordering", "catalogue"]
_TURNED_OFF = ("ux", "bdd")
_CATALOGUE_BOOK = """from __future__ import annotations


@aggregate_root
@entity
class Book:
    \"\"\"Module: Catalogue | custom · Book\"\"\"

    bookId: BookId

    def __init__(self, bookId: BookId) -> None:
        self.bookId = bookId


@repository
class BookRepository:
    \"\"\"Module: Catalogue | custom · Book\"\"\"

    def create(self, bookId: BookId) -> Book:
        raise NotImplementedError
"""
# What the server answers a call that outlives the seconds it waits for it.
_STILL_RUNNING = "is still running after"


class Pinging:
    """A chat that asks the server small things for as long as builds run, timing every answer, and a crowd of other
    chats that keep asking a small graph tool meanwhile."""

    def __init__(self, server: SpecServer) -> None:
        self.server = server
        self.answers: list[tuple[str, float]] = []

    async def ask_while(self, built: anyio.Event) -> None:
        async with anyio.create_task_group() as group:
            group.start_soon(self._ask, built)
            for _ in range(_CROWD):
                group.start_soon(self._crowd, built)

    async def _ask(self, built: anyio.Event) -> None:
        async with self.server.chat(_project("asker"), 60) as asker:
            while not built.is_set():
                for tool in ("cdd.ping", "graph.practice_names"):
                    started = time.monotonic()
                    await asker.call_tool(tool, arguments={})
                    self.answers.append((tool, time.monotonic() - started))
                await anyio.sleep(_PING_EVERY_SECONDS)

    async def _crowd(self, built: anyio.Event) -> None:
        async with self.server.chat(_project("board"), 60) as page:
            while not built.is_set():
                await page.call_tool("graph.practice_names", arguments={})
                await anyio.sleep(_PING_EVERY_SECONDS)

    @property
    def slowest(self) -> float:
        return max(seconds for _tool, seconds in self.answers)

    @property
    def median(self) -> float:
        return statistics.median(seconds for _tool, seconds in self.answers)


class BuildsWhilePinging:
    """Several chats build the graph at once, each on a project of its own, while others ask the server small things."""

    def __init__(self, server: SpecServer) -> None:
        self.server = server
        self.pinging = Pinging(server)
        self.build_results: list[str] = []
        self.progress_reports = 0

    def run(self, databases: list[Path]) -> None:
        asyncio.run(self._run(databases))

    async def _run(self, databases: list[Path]) -> None:
        built = anyio.Event()
        async with anyio.create_task_group() as group:
            group.start_soon(self._build_all, databases, built)
            group.start_soon(self.pinging.ask_while, built)

    async def _build_all(self, databases: list[Path], built: anyio.Event) -> None:
        async with anyio.create_task_group() as builds:
            for database in databases:
                builds.start_soon(self._build, database)
        built.set()

    async def _build(self, database: Path) -> None:
        async with self.server.chat(_project("builder"), _BUILD_SECONDS) as builder:
            arguments = {"folder": str(_REPO_ROOT), "practices": _PRACTICES, "database": str(database), "force": True}
            result = await builder.call_tool("graph.load_working_copy", arguments=arguments, progress_callback=self._heard)
            self.build_results.append(result.content[0].text)

    async def _heard(self, _progress: float, _total: float | None, _message: str | None) -> None:
        self.progress_reports += 1


class RefreshesWhilePinging:
    """Six chats on one project refresh the graph its session holds at once, each with its own files, round after round,
    while others ask the server small things. The graph is loaded with every practice first."""

    def __init__(self, server: SpecServer, project: Path) -> None:
        self.server = server
        self.project = project
        self.pinging = Pinging(server)
        self.loaded = ""
        self.refresh_results: list[str] = []
        self.refresh_seconds: list[float] = []

    def run(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        async with self.server.chat(self.project, _BUILD_SECONDS) as loader:
            practices = {key: "." for key in _PRACTICE_KEYS}
            arguments = {"folder": str(self.project), "practices": practices, "force": True}
            self.loaded = (await loader.call_tool("graph.load_working_copy", arguments=arguments)).content[0].text
        refreshed = anyio.Event()
        async with anyio.create_task_group() as group:
            group.start_soon(self._refresh_all, refreshed)
            group.start_soon(self.pinging.ask_while, refreshed)

    async def _refresh_all(self, refreshed: anyio.Event) -> None:
        async with anyio.create_task_group() as validators:
            for files in _VALIDATED:
                validators.start_soon(self._validate, files)
        refreshed.set()

    async def _validate(self, files: tuple[str, ...]) -> None:
        async with self.server.chat(self.project, _BUILD_SECONDS) as validator:
            for _round in range(_ROUNDS):
                started = time.monotonic()
                answer = await self._refreshed(validator, files)
                self.refresh_seconds.append(time.monotonic() - started)
                self.refresh_results.append(answer)

    async def _refreshed(self, validator, files: tuple[str, ...]) -> str:
        """The refresh's answer: a call that outlives the seconds the server waits is called again, which waits for the
        run already going, as an agent does."""
        while True:
            result = await validator.call_tool("graph.refresh", arguments={"paths": list(files)})
            answer = result.content[0].text
            if _STILL_RUNNING not in answer:
                return f"{' '.join(files)}: {answer}"


class ValidatesWhilePinging(RefreshesWhilePinging):
    """Six chats on one project validate their own files with the session's graph at once, round after round, while
    others ask the server small things: the live path agents take, whose refresh and checked nodes the graph's worker
    writes. The graph is loaded with every practice first."""

    async def _refreshed(self, validator, files: tuple[str, ...]) -> str:
        """Whether the validate answered with its graph report: a call that outlives the seconds the server waits is
        called again, as an agent does."""
        arguments = {"guidance": _VALIDATED_GUIDANCE, "graph": True, "paths": list(files)}
        while True:
            result = await validator.call_tool("validate.validate", arguments=arguments)
            answer = result.content[0].text
            if _STILL_RUNNING not in answer:
                return f"{' '.join(files)}: {'graph' in answer and not result.isError}"


class PracticeRootsLoad:
    """A session in a copy of the Bookshop project whose practices work in three different folders, its graph loaded
    from those roots as the Graph app loads it, and then from the same files named to ``graph.load_files``: the node
    ids each load saved, by practice."""

    def __init__(self, server: SpecServer) -> None:
        self.server = server
        self.project = Path(tempfile.mkdtemp(prefix="cdd-practice-roots-")) / "bookshop"
        shutil.copytree(_BOOKSHOP, self.project)
        book = self.project / "catalogue" / "book" / "book.py"
        book.parent.mkdir(parents=True)
        book.write_text(_CATALOGUE_BOOK, encoding="utf-8")
        record = self.project / ".sessions" / "main"
        record.mkdir(parents=True)
        outputs = {key: {"root": root} for key, root in _SESSION_ROOTS.items()}
        outputs["ddd"]["tactics"] = {"roots": _TACTICS_ROOTS}
        fields = {"name": "main", "outputs": outputs, "practices": {key: {"enabled": False} for key in _TURNED_OFF}}
        (record / "session.json").write_text(json.dumps(fields), encoding="utf-8")
        self.loaded = ""
        self.from_roots: dict[str, set[str]] = {}
        self.from_files: dict[str, set[str]] = {}

    def run(self) -> None:
        asyncio.run(self._run())

    async def _run(self) -> None:
        async with self.server.chat(self.project, _BUILD_SECONDS) as chat:
            self.loaded = (await chat.call_tool("graph.load_practice_roots", arguments={})).content[0].text
            self.from_roots = await self._saved_nodes(chat)
            files = sorted({*_SESSION_ROOTS.values(), *_TACTICS_ROOTS})
            arguments = {"folder": str(self.project), "practices": list(_SESSION_ROOTS), "files": files}
            await chat.call_tool("graph.load_files", arguments=arguments)
            self.from_files = await self._saved_nodes(chat)

    async def _saved_nodes(self, chat) -> dict[str, set[str]]:
        """The id of every node the session's graph holds now, by practice, read from the file ``graph.save_json``
        names."""
        saved = json.loads((await chat.call_tool("graph.save_json", arguments={})).content[0].text)["path"]
        practices = json.loads(Path(saved).read_text(encoding="utf-8"))["practices"]
        return {key: {node["node_id"] for node in practice["nodes"]} for key, practice in practices.items()}

    def nodes_of(self, key: str, type: str, loaded: dict[str, set[str]]) -> list[str]:
        return sorted(node for node in loaded.get(key, set()) if node.startswith(f"{key}:{type}:"))

    def close(self) -> None:
        shutil.rmtree(self.project.parent, ignore_errors=True)


class AllAtOnce:
    """The four runs this spec checks, each on a server and a project of its own, started together and waited for: the
    builds, the refreshes, the validates, and the Graph app's whole load. The servers start one after another, since
    starting one names it in this process's environment, which the server copies; the runs then go on side by side.
    Each context reads its own run, and stops its own server when it is done with it."""

    def __init__(self) -> None:
        self.builds_server = self._started(_TOOLSETS)
        self.databases = [Path(tempfile.mkdtemp(prefix="cdd-graph-database-")) for _ in range(_BUILDERS)]
        self.builds = BuildsWhilePinging(self.builds_server)
        self.refresh_server = self._started(_TOOLSETS)
        self.refresh_project = _practices_copy()
        self.refreshes = RefreshesWhilePinging(self.refresh_server, self.refresh_project)
        self.validate_server = self._started(_VALIDATE_TOOLSETS)
        self.validate_project = _practices_copy()
        self.validates = ValidatesWhilePinging(self.validate_server, self.validate_project)
        self.roots_server = self._started(_VALIDATE_TOOLSETS)
        self.roots = PracticeRootsLoad(self.roots_server)
        self.seconds: dict[str, float] = {}
        self.failures: dict[str, BaseException] = {}
        runs = {"builds": lambda: self.builds.run(self.databases), "refreshes": self.refreshes.run, "validates": self.validates.run, "roots": self.roots.run}
        threads = [threading.Thread(target=self._timed, args=(name, run), name=f"graph-build-{name}") for name, run in runs.items()]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

    def outcome(self, name: str) -> None:
        """Raise the failure the named run met, so each of its context's examples reports it."""
        if name in self.failures:
            raise self.failures[name]

    def _timed(self, name: str, run) -> None:
        started = time.monotonic()
        try:
            run()
        except BaseException as failure:  # The context that reads this run raises it in its own setup.
            self.failures[name] = failure
        self.seconds[name] = time.monotonic() - started

    @staticmethod
    def _started(toolsets: tuple[str, ...]) -> SpecServer:
        server = SpecServer(toolsets)
        server.start()
        return server


_ALL_AT_ONCE: list[AllAtOnce] = []


def _all_at_once() -> AllAtOnce:
    """The four runs, started by the first context that asks for them."""
    if not _ALL_AT_ONCE:
        _ALL_AT_ONCE.append(AllAtOnce())
    return _ALL_AT_ONCE[0]


def _project(role: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"cdd-{role}-"))


def _practices_copy() -> Path:
    """A copy of ``cdd_guidance/practices`` in a folder of its own, which the shared graph is loaded from and saved in;
    the examples and the repository story map snapshot a spec edits are left out, whose deep folders pass the longest
    path Windows takes."""
    folder = Path(tempfile.mkdtemp(prefix="cdd-shared-graph-")) / "practices"
    shutil.copytree(_REPO_ROOT / "cdd_guidance" / "practices", folder, ignore=shutil.ignore_patterns("_examples", "repository-story-map", "node_modules", "__pycache__"))
    return folder


with description("the cdd server while several chats build a graph at once") as self:
    with before.all:
        runs = _all_at_once()
        self.server = runs.builds_server
        self.databases = runs.databases
        self.probe = runs.builds
        runs.outcome("builds")

    with after.all:
        self.server.stop()
        for database in self.databases:
            shutil.rmtree(database, ignore_errors=True)

    with it("should finish every build"):
        expect(self.probe.build_results).to(equal([_LOADED] * _BUILDERS))

    with it("should save each build's graph, which its worker writes"):
        expect([(database / ".context" / "graph.json").is_file() for database in self.databases]).to(equal([True] * _BUILDERS))

    with it("should be asked while the builds run"):
        expect(len(self.probe.pinging.answers)).to(be_above(4))

    with it("should tell each chat that builds how its build goes"):
        expect(self.probe.progress_reports).to(be_above(_BUILDERS))

    # Skipped: the slowest answer runs 2.2 to 2.9 s on the release machine, and the user chose not to hold a release on it.
    with _it("should answer every call within two seconds while the builds run"):
        expect(self.probe.pinging.slowest).to(be_below(_ANSWER_WITHIN_SECONDS))


with description("the cdd server while several chats refresh the one graph their session holds") as self:
    with before.all:
        runs = _all_at_once()
        self.server = runs.refresh_server
        self.project = runs.refresh_project
        self.probe = runs.refreshes
        runs.outcome("refreshes")
        pinging = self.probe.pinging
        print(
            f"\n{len(self.probe.refresh_results)} refreshes in {runs.seconds['refreshes']:.0f} s; each took "
            f"{statistics.median(self.probe.refresh_seconds):.1f} s at the median; {len(pinging.answers)} answers, median "
            f"{pinging.median:.2f} s, slowest {pinging.slowest:.2f} s"
        )

    # A setup that failed part way leaves some of these unset; cleaning up only what it made keeps its error the one
    # each example reports.
    with after.all:
        if getattr(self, "server", None) is not None:
            self.server.stop()
        if getattr(self, "project", None) is not None:
            shutil.rmtree(self.project.parent, ignore_errors=True)

    with it("should load every practice into the shared graph first"):
        expect(self.probe.loaded).to(equal(_LOADED))

    with it("should finish every refresh"):
        expected = [f'{" ".join(files)}: {{"message": "Refreshed {len(files)} files."}}' for files in _VALIDATED for _round in range(_ROUNDS)]
        expect(sorted(self.probe.refresh_results)).to(equal(sorted(expected)))

    with it("should be asked while the refreshes run"):
        expect(len(self.probe.pinging.answers)).to(be_above(4))

    with it("should answer every call within two seconds while the refreshes run"):
        expect(self.probe.pinging.slowest).to(be_below(_ANSWER_WITHIN_SECONDS))


with description("the cdd server while several chats validate files of the one graph their session holds") as self:
    with before.all:
        runs = _all_at_once()
        self.server = runs.validate_server
        self.project = runs.validate_project
        self.probe = runs.validates
        runs.outcome("validates")
        pinging = self.probe.pinging
        print(
            f"\n{len(self.probe.refresh_results)} validates in {runs.seconds['validates']:.0f} s; each took "
            f"{statistics.median(self.probe.refresh_seconds):.1f} s at the median; {len(pinging.answers)} answers, median "
            f"{pinging.median:.2f} s, slowest {pinging.slowest:.2f} s"
        )

    # A setup that failed part way leaves some of these unset; cleaning up only what it made keeps its error the one
    # each example reports.
    with after.all:
        if getattr(self, "server", None) is not None:
            self.server.stop()
        if getattr(self, "project", None) is not None:
            shutil.rmtree(self.project.parent, ignore_errors=True)

    with it("should load every practice into the shared graph first"):
        expect(self.probe.loaded).to(equal(_LOADED))

    with it("should answer every validate with its graph report"):
        expected = [f"{' '.join(files)}: True" for files in _VALIDATED for _round in range(_ROUNDS)]
        expect(sorted(self.probe.refresh_results)).to(equal(sorted(expected)))

    with it("should be asked while the validates run"):
        expect(len(self.probe.pinging.answers)).to(be_above(4))

    with it("should answer every call within two seconds while the validates run"):
        expect(self.probe.pinging.slowest).to(be_below(_ANSWER_WITHIN_SECONDS))


# Exploratory testing, r3-cog-03: the Graph app's load of a session with all five practices left out every story test
# in code and the DDD root's own tactics code, read no root added to a fidelity, and named each node's file from its
# practice's root.
with description("the Graph app's whole load of a session whose practices work in different folders") as self:
    with before.all:
        runs = _all_at_once()
        self.server = runs.roots_server
        self.load = runs.roots
        runs.outcome("roots")

    with after.all:
        if getattr(self, "server", None) is not None:
            self.server.stop()
        if getattr(self, "load", None) is not None:
            self.load.close()

    with it("should hold, for each practice, the nodes a load of the same files holds"):
        differing = {
            key: (sorted(self.load.from_files[key] - nodes), sorted(nodes - self.load.from_files[key]))
            for key, nodes in self.load.from_roots.items()
            if nodes != self.load.from_files.get(key)
        }
        expect(differing).to(equal({}))

    with it("should hold the scenarios of the story tests written in code"):
        scenarios = self.load.nodes_of("stories", "Scenario", self.load.from_roots)
        expect([node for node in scenarios if ".test.py:" in node or ".test.ts:" in node]).not_to(equal([]))

    with it("should read the DDD root's own tactics code, naming each file from the project's root"):
        expect(self.load.nodes_of("ddd", "EntityRoot", self.load.from_roots)).to(contain("ddd:EntityRoot:ordering/order/order.py:Order"))

    with it("should read the folder added to DDD's tactics"):
        expect(self.load.nodes_of("ddd", "EntityRoot", self.load.from_roots)).to(contain("ddd:EntityRoot:catalogue/book/book.py:Book"))
