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
chat calls ``cdd.ping`` and that tool every half second for as long as any build runs, timing every answer."""

import asyncio
import shutil
import statistics
import sys
import tempfile
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import anyio
from expects import be_above, be_below, equal, expect
from mamba import after, before, description, it

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
    ("clean_engineering/model/operation.py", "clean_engineering/rules/class_graph.py"),
    ("stories/model/story_model.py", "stories/stories.py"),
    ("ddd/model/nodes.py", "ddd/model/graph_reading.py"),
    ("bdd/model/graph_bdd_model_spec.py", "bdd/model/graph_reading.py"),
    ("ux/model/story_link.py", "ux/model/nodes.py"),
    ("clean_engineering/model/graph_reading.py", "stories/model/graph_reading.py"),
)
# How many times each validator refreshes its files.
_ROUNDS = 2
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


def _project(role: str) -> Path:
    return Path(tempfile.mkdtemp(prefix=f"cdd-{role}-"))


def _practices_copy() -> Path:
    """A copy of ``cdd_guidance/practices`` in a folder of its own, which the shared graph is loaded from and saved in;
    the examples are left out, whose deep folders pass the longest path Windows takes."""
    folder = Path(tempfile.mkdtemp(prefix="cdd-shared-graph-")) / "practices"
    shutil.copytree(_REPO_ROOT / "cdd_guidance" / "practices", folder, ignore=shutil.ignore_patterns("_examples", "node_modules", "__pycache__"))
    return folder


with description("the cdd server while several chats build a graph at once") as self:
    with before.all:
        self.server = SpecServer(_TOOLSETS)
        self.server.start()
        self.databases = [Path(tempfile.mkdtemp(prefix="cdd-graph-database-")) for _ in range(_BUILDERS)]
        self.probe = BuildsWhilePinging(self.server)
        self.probe.run(self.databases)

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

    with it("should answer every call within two seconds while the builds run"):
        expect(self.probe.pinging.slowest).to(be_below(_ANSWER_WITHIN_SECONDS))


with description("the cdd server while several chats refresh the one graph their session holds") as self:
    with before.all:
        self.server = SpecServer(_TOOLSETS)
        self.server.start()
        self.project = _practices_copy()
        self.probe = RefreshesWhilePinging(self.server, self.project)
        started = time.monotonic()
        self.probe.run()
        pinging = self.probe.pinging
        print(
            f"\n{len(self.probe.refresh_results)} refreshes in {time.monotonic() - started:.0f} s; each took "
            f"{statistics.median(self.probe.refresh_seconds):.1f} s at the median; {len(pinging.answers)} answers, median "
            f"{pinging.median:.2f} s, slowest {pinging.slowest:.2f} s"
        )

    with after.all:
        self.server.stop()
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
        self.server = SpecServer(_VALIDATE_TOOLSETS)
        self.server.start()
        self.project = _practices_copy()
        self.probe = ValidatesWhilePinging(self.server, self.project)
        started = time.monotonic()
        self.probe.run()
        pinging = self.probe.pinging
        print(
            f"\n{len(self.probe.refresh_results)} validates in {time.monotonic() - started:.0f} s; each took "
            f"{statistics.median(self.probe.refresh_seconds):.1f} s at the median; {len(pinging.answers)} answers, median "
            f"{pinging.median:.2f} s, slowest {pinging.slowest:.2f} s"
        )

    with after.all:
        self.server.stop()
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
