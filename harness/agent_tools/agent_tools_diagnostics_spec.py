"""MCP tools diagnostics — ping and invoke workspace toolsets (space, harness, tools)."""
import asyncio
import json
import os
import shutil
import sys
import tempfile
import time
from datetime import timedelta
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from harness.installation.installer import Installer

Installer(repo=_REPO_ROOT).ensure_import_path()

from expects import contain, equal, expect
from mamba import description, it

from harness.agent_tools.agent_tools_diagnostics import AgentToolsDiagnostics
from harness.mcp.mcp_server import McpHost, McpOperationDefinition
from harness.agent_tools.agent_tools_probe import (
    AGENT_TOOLS_PROBE_SECTION,
    agent_tools_toolset_ref,
    probe_agent_tools_standalone,
    published_agent_tools_mcp,
)

_AGENT_TOOLS_DIAGNOSTICS_REF = (
    "harness.agent_tools.agent_tools_diagnostics:AgentToolsDiagnostics"
)
_VENV_PYTHON = _REPO_ROOT / ".venv" / "Scripts" / "python.exe"
_PYTHON = _VENV_PYTHON if _VENV_PYTHON.is_file() else Path(sys.executable)


def _stdio_params(toolsets: str) -> StdioServerParameters:
    return StdioServerParameters(
        command=str(_PYTHON),
        args=["-m", "harness.mcp", "--toolsets", toolsets],
        cwd=str(_REPO_ROOT),
        env={
            **os.environ,
            "PYTHONPYCACHEPREFIX": str(_REPO_ROOT / ".pycache"),
            "CDD_REPO": str(_REPO_ROOT),
            "CDD_PROJECT": str(_REPO_ROOT),
        },
    )


async def _call_agent_tools_diagnostics_stdio() -> tuple[float, str]:
    async with stdio_client(_stdio_params(_AGENT_TOOLS_DIAGNOSTICS_REF)) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(
            read_stream,
            write_stream,
            read_timeout_seconds=timedelta(seconds=150),
        ) as session:
            await session.initialize()
            started = time.perf_counter()
            result = await session.call_tool(
                "agent-tools-diagnostics.agent_tools_diagnostics",
                arguments={},
            )
            elapsed = time.perf_counter() - started
            return elapsed, result.content[0].text


def _installer(
    tree: Path,
    mcp_items: list[str],
    toolset_items: list[str] | None = None,
) -> Installer:
    installer = Installer(ide="Cursor", path=tree, repo=_REPO_ROOT)
    log = installer._diagnostics_log()
    entry: dict = {"mcp": {"items": mcp_items}}
    if toolset_items is not None:
        entry["toolset"] = {"items": toolset_items}
    log.write_text(json.dumps({"installs": [entry]}, indent=2), encoding="utf-8")
    return installer


with description("mcp tools diagnostics"):
    with it("should scope toolsets to space, harness, and tools only"):
        expect(agent_tools_toolset_ref("space.repo.repo:Repo")).to(equal(True))
        expect(agent_tools_toolset_ref("harness.graph.graph:Graph")).to(equal(True))
        expect(agent_tools_toolset_ref("tools.echo.echo:Echo")).to(equal(True))
        expect(agent_tools_toolset_ref("cdd_guidance.practices.bdd.bdd:Bdd")).to(equal(False))
        expect(agent_tools_toolset_ref("cdd_guidance.builders.create_agent_toolset.create_agent_toolset:CreateAgentToolset")).to(
            equal(False)
        )
        expect(agent_tools_toolset_ref("harness.guidance.guidance:Guidance")).to(equal(False))
        expect(agent_tools_toolset_ref("harness.guidance.guidance_diagnostics:GuidanceDiagnostics")).to(
            equal(False)
        )
        expect(agent_tools_toolset_ref("harness.guidance_actions.guidance_actions:GuidanceAction")).to(
            equal(False)
        )
        expect(agent_tools_toolset_ref("harness.graph.graph:Graph")).to(equal(True))

    with it("should enroll agent-tools-diagnostics as an MCP tool not a prompt"):
        host = McpHost.from_refs(
            (_AGENT_TOOLS_DIAGNOSTICS_REF,),
            repo=str(_REPO_ROOT),
            project=str(_REPO_ROOT),
        )
        name = "agent-tools-diagnostics.agent_tools_diagnostics"
        expect(name in host._runtime._tools).to(equal(True))
        expect(name in host._runtime._prompts).to(equal(False))

    with it("should treat agent_tools_diagnostics as kind tool for MCP enrollment"):
        tool = AgentToolsDiagnostics().tools["agent_tools_diagnostics"]
        expect(tool.kind).to(equal("tool"))
        expect(McpOperationDefinition.from_tool(tool).kind).to(equal("tool"))

    with it("should complete agent-tools-diagnostics over stdio MCP within two minutes"):
        elapsed, text = asyncio.run(_call_agent_tools_diagnostics_stdio())
        expect(elapsed < 120.0).to(equal(True))
        expect("green" in text.split("\n")[0]).to(equal(True))
        expect("deferred on the stdio host" in text).to(equal(False))
        expect("invoke:" in text).to(equal(True))

    with it("should never publish nested diagnostics tools as workspace probe targets"):
        tree = Path(tempfile.mkdtemp())
        try:
            installer = _installer(
                tree,
                [
                    "repo.switch_branch",
                    "agent-tools-diagnostics.agent_tools_diagnostics",
                    "guidance-diagnostics.guidance_diagnostics",
                ],
                toolset_items=["space.repo.repo:Repo"],
            )
            scoped = published_agent_tools_mcp(installer)
            expect(scoped).to(contain("repo.switch_branch"))
            expect(scoped).not_to(contain("agent-tools-diagnostics.agent_tools_diagnostics"))
            expect(scoped).not_to(contain("guidance-diagnostics.guidance_diagnostics"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

    with it("should list repo.switch_branch in published workspace MCP names"):
        tree = Path(tempfile.mkdtemp())
        try:
            installer = _installer(
                tree,
                ["repo.switch_branch", "bdd-behavior", "cdd.ping"],
                toolset_items=["space.repo.repo:Repo"],
            )
            scoped = published_agent_tools_mcp(installer)
            expect(scoped).to(equal(["repo.switch_branch"]))
            expect(scoped).not_to(contain("bdd-behavior"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

    with it("should write agent_tools with ping and invoke sections"):
        tree = Path(tempfile.mkdtemp())
        try:
            installer = _installer(
                tree,
                ["repo.switch_branch", "bdd-behavior", "cdd.ping"],
                toolset_items=["space.repo.repo:Repo"],
            )
            report = probe_agent_tools_standalone(installer)
            expect("green" in report.split("\n")[0]).to(equal(True))
            data = json.loads((tree / "diagnostics.json").read_text(encoding="utf-8"))
            section = data[AGENT_TOOLS_PROBE_SECTION]
            expect("ping" in section).to(equal(True))
            expect("invoke" in section).to(equal(True))
            names = [item["mcp"] for item in section["ping"]["items"]]
            expect(names).to(contain("repo.switch_branch"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

    with it("should install agent-tools-diagnostics as slash command with MCP invoke"):
        tree = Path(tempfile.mkdtemp())
        try:
            mcp = Installer(ide="Cursor", path=tree, repo=_REPO_ROOT).install(
                [AgentToolsDiagnostics()]
            )
            path = tree / "commands" / "harness" / "agent-tools" / "agent-tools-diagnostics.md"
            expect(path.is_file()).to(equal(True))
            text = path.read_text(encoding="utf-8")
            expect(text).to(contain("agent-tools-diagnostics.agent_tools_diagnostics"))
            expect(text).to(contain("agent_tools"))
            names = [op.mcp_name for op in mcp.mcp_operations]
            expect(names).to(contain("agent-tools-diagnostics.agent_tools_diagnostics"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)
