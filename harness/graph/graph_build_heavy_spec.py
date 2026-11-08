"""Infrastructure spec: the cdd server keeps answering every chat while a chat's graph build runs.

A graph build is minutes of CPU-bound Python. Run in the server's own interpreter, it slowed the event loop until the
server stopped accepting connections and every chat lost its cdd tools. This spec starts a server of its own, on a port
of its own, and builds every practice's graph of ``cdd_guidance/practices`` from one chat, which asks to hear the build's
progress as Claude Code does. Meanwhile a crowd of other chats, as the Session Board's open pages are, keep asking a
small graph tool, and one more chat calls ``cdd.ping`` and that tool every half second for as long as the build runs."""

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
# How many other chats keep asking while the build runs, as the Session Board's pages do.
_CROWD = 20
_ANSWER_WITHIN_SECONDS = 2
_BUILD_SECONDS = 900


class BuildWhilePinging:
    """One chat builds the graph while another asks the server small things, timing every answer."""

    def __init__(self, server: SpecServer) -> None:
        self.server = server
        self.answers: list[tuple[str, float]] = []
        self.build_seconds = 0.0
        self.build_result = ""
        self.progress_reports = 0

    def run(self, database: Path) -> None:
        asyncio.run(self._run(database))

    async def _run(self, database: Path) -> None:
        built = anyio.Event()
        async with anyio.create_task_group() as group:
            group.start_soon(self._build, database, built)
            group.start_soon(self._ask, built)
            for _ in range(_CROWD):
                group.start_soon(self._crowd, built)

    async def _build(self, database: Path, built: anyio.Event) -> None:
        async with self.server.chat(self._project("builder"), _BUILD_SECONDS) as builder:
            started = time.monotonic()
            arguments = {"folder": str(_REPO_ROOT), "practices": _PRACTICES, "database": str(database), "force": True}
            result = await builder.call_tool("graph.load_working_copy", arguments=arguments, progress_callback=self._heard)
            self.build_result = result.content[0].text
            self.build_seconds = time.monotonic() - started
            built.set()

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


with description("the cdd server while a chat builds a graph") as self:
    with before.all:
        self.server = SpecServer(_TOOLSETS)
        self.server.start()
        self.database = Path(tempfile.mkdtemp(prefix="cdd-graph-database-"))
        self.probe = BuildWhilePinging(self.server)
        self.probe.run(self.database)

    with after.all:
        self.server.stop()
        shutil.rmtree(self.database, ignore_errors=True)

    with it("should finish the build"):
        expect(self.probe.build_result).to(equal('{"message": "Loaded the working copies."}'))

    with it("should be asked while the build runs"):
        expect(len(self.probe.answers)).to(be_above(4))

    with it("should tell the chat that builds how the build goes"):
        expect(self.probe.progress_reports).to(be_above(0))

    with it("should answer every call within two seconds while the build runs"):
        expect(self.probe.slowest).to(be_below(_ANSWER_WITHIN_SECONDS))
