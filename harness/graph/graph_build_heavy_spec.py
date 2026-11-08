"""Infrastructure spec: the cdd server keeps answering every chat while several chats' graph builds run.

A graph build is minutes of CPU-bound Python. Run in the server's own interpreter, it slowed the event loop until the
server stopped accepting connections and every chat lost its cdd tools. This spec starts a server of its own, on a port
of its own, and has five chats, each on a project of its own, build every practice's graph of ``cdd_guidance/practices``
at once, as several agents' validates do; each asks to hear its build's progress as Claude Code does. Meanwhile a crowd
of other chats, as the Session Board's open pages are, keep asking a small graph tool, and one more chat calls
``cdd.ping`` and that tool every half second for as long as any build runs."""

import asyncio
import shutil
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
_PRACTICES = {key: "cdd_guidance/practices" for key in ("stories", "ddd", "ux", "clean_engineering", "bdd")}
_PING_EVERY_SECONDS = 0.5
# How many chats build a graph at once, each on a project of its own.
_BUILDERS = 5
# How many other chats keep asking while the builds run, as the Session Board's pages do.
_CROWD = 20
_ANSWER_WITHIN_SECONDS = 2
_BUILD_SECONDS = 900
_LOADED = '{"message": "Loaded the working copies."}'


class BuildsWhilePinging:
    """Several chats build the graph at once while another asks the server small things, timing every answer."""

    def __init__(self, server: SpecServer) -> None:
        self.server = server
        self.answers: list[tuple[str, float]] = []
        self.build_results: list[str] = []
        self.progress_reports = 0

    def run(self, databases: list[Path]) -> None:
        asyncio.run(self._run(databases))

    async def _run(self, databases: list[Path]) -> None:
        built = anyio.Event()
        async with anyio.create_task_group() as group:
            group.start_soon(self._build_all, databases, built)
            group.start_soon(self._ask, built)
            for _ in range(_CROWD):
                group.start_soon(self._crowd, built)

    async def _build_all(self, databases: list[Path], built: anyio.Event) -> None:
        async with anyio.create_task_group() as builds:
            for database in databases:
                builds.start_soon(self._build, database)
        built.set()

    async def _build(self, database: Path) -> None:
        async with self.server.chat(self._project("builder"), _BUILD_SECONDS) as builder:
            arguments = {"folder": str(_REPO_ROOT), "practices": _PRACTICES, "database": str(database), "force": True}
            result = await builder.call_tool("graph.load_working_copy", arguments=arguments, progress_callback=self._heard)
            self.build_results.append(result.content[0].text)

    async def _heard(self, _progress: float, _total: float | None, _message: str | None) -> None:
        self.progress_reports += 1

    async def _ask(self, built: anyio.Event) -> None:
        async with self.server.chat(self._project("asker"), 60) as asker:
            while not built.is_set():
                for tool in ("cdd.ping", "graph.practice_names"):
                    started = time.monotonic()
                    await asker.call_tool(tool, arguments={})
                    self.answers.append((tool, time.monotonic() - started))
                await anyio.sleep(_PING_EVERY_SECONDS)

    async def _crowd(self, built: anyio.Event) -> None:
        async with self.server.chat(self._project("board"), 60) as page:
            while not built.is_set():
                await page.call_tool("graph.practice_names", arguments={})
                await anyio.sleep(_PING_EVERY_SECONDS)

    def _project(self, role: str) -> Path:
        return Path(tempfile.mkdtemp(prefix=f"cdd-{role}-"))

    @property
    def slowest(self) -> float:
        return max(seconds for _tool, seconds in self.answers)


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
        expect(len(self.probe.answers)).to(be_above(4))

    with it("should tell each chat that builds how its build goes"):
        expect(self.probe.progress_reports).to(be_above(_BUILDERS))

    with it("should answer every call within two seconds while the builds run"):
        expect(self.probe.slowest).to(be_below(_ANSWER_WITHIN_SECONDS))
