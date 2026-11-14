"""MCP tools diagnostics called by a chat through a real cdd server, and installed from the repository. Heavy: starts the
server in its own process, and an install stands up every toolset the repository has."""
import asyncio
import shutil
import sys
import tempfile
import time
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.installer import Installer
from harness.installation.repository_toolsets import RepositoryToolsets

RepositoryToolsets(_REPO_ROOT).ensure_import_path()

from expects import contain, equal, expect
from mamba import after, before, context, description, it
from space.session.throwaway_project import ThrowawayProject

from harness.diagnostics.agent_tools_diagnostics import AgentToolsDiagnostics
from harness.mcp.mcp_server import McpInstallation
from harness.mcp.spec_support import SpecServer

_AGENT_TOOLS_DIAGNOSTICS_REF = "harness.diagnostics.agent_tools_diagnostics:AgentToolsDiagnostics"
_DIAGNOSTICS_SECONDS = 150


def _call_agent_tools_diagnostics(project: Path) -> tuple[float, str]:
    """Run the diagnostics tool through a real cdd server, as a chat working on the spec's own project does."""
    server = SpecServer((_AGENT_TOOLS_DIAGNOSTICS_REF,))
    server.start()
    try:
        return asyncio.run(_timed_diagnostics(server, project))
    finally:
        server.stop()


async def _timed_diagnostics(server: SpecServer, project: Path) -> tuple[float, str]:
    async with server.chat(project, _DIAGNOSTICS_SECONDS) as session:
        started = time.perf_counter()
        result = await session.call_tool("agent-tools-diagnostics.agent_tools_diagnostics", arguments={})
        return time.perf_counter() - started, result.content[0].text


with description("mcp tools diagnostics"):
    with it("should install agent-tools-diagnostics as slash command with MCP invoke"):
        tree = Path(tempfile.mkdtemp())
        try:
            mcp = Installer(ide="Cursor", path=tree, repo=_REPO_ROOT).install(
                [AgentToolsDiagnostics()]
            ).of(McpInstallation)
            path = tree / "commands" / "harness" / "diagnostics" / "agent-tools-diagnostics.md"
            expect(path.is_file()).to(equal(True))
            text = path.read_text(encoding="utf-8")
            expect(text).to(contain("agent-tools-diagnostics.agent_tools_diagnostics"))
            expect(text).to(contain("agent_tools"))
            names = [op.mcp_name for op in mcp.mcp_operations]
            expect(names).to(contain("agent-tools-diagnostics.agent_tools_diagnostics"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

    # A chat on a project with nothing installed probes nothing, so its ping phase is red; the call still completes.
    with context("that a chat calls through the cdd server"):
        # Every example here only reads the one call's answer, so the server is started and called once for them all.
        # Actions log to the open session, so the call works on its own project rather than this repository's.
        with before.all:
            self.project = ThrowawayProject()
            self.elapsed, self.text = _call_agent_tools_diagnostics(self.project.root)

        with after.all:
            ThrowawayProject.close_all()

        with it("should complete within two minutes"):
            expect(self.elapsed < 120.0).to(equal(True))

        with it("should report the invoke phase"):
            expect(self.text).to(contain("invoke:"))
