"""MCP tools diagnostics — ping and invoke workspace toolsets (space, harness, tools)."""
import json
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

from expects import contain, equal, expect, have_key
from mamba import after, before, context, description, it
from space.session.throwaway_project import ThrowawayProject

from harness.diagnostics import agent_tools_probe
from harness.diagnostics.agent_tools_diagnostics import AgentToolsDiagnostics
from harness.mcp._examples.call_outcomes.call_outcomes import MONTH_END_SECONDS
from harness.mcp.mcp_server import McpHost
from harness.diagnostics.agent_tools_probe import (
    AGENT_TOOLS_PROBE_SECTION,
    AgentToolsProbe,
    agent_tools_toolset_ref,
)

_AGENT_TOOLS_DIAGNOSTICS_REF = (
    "harness.diagnostics.agent_tools_diagnostics:AgentToolsDiagnostics"
)
_REPO_TOOLSET = "space.repo.repo:Repo"
_CALL_OUTCOMES = "harness.mcp._examples.call_outcomes.call_outcomes:CallOutcomes"


def _host_of(*refs: str) -> McpHost:
    return McpHost.from_refs(refs, repo=str(_REPO_ROOT), project=str(_REPO_ROOT))


def _installer(
    tree: Path,
    mcp_items: list[str],
    toolset_items: list[str] | None = None,
) -> Installer:
    installer = Installer(ide="Cursor", path=tree, repo=_REPO_ROOT)
    log = installer.diagnostics.path
    entry: dict = {"mcp": {"items": mcp_items}}
    if toolset_items is not None:
        entry["toolset"] = {"items": toolset_items}
    log.write_text(json.dumps({"installs": [entry]}, indent=2), encoding="utf-8")
    return installer


with description("mcp tools diagnostics"):
    # Actions log to the open session, so each example works on its own project rather than this repository's.
    with before.each:
        self.project = ThrowawayProject()

    with after.each:
        ThrowawayProject.close_all()

    with it("should scope toolsets to space, harness, and tools only"):
        expect(agent_tools_toolset_ref("space.repo.repo:Repo")).to(equal(True))
        expect(agent_tools_toolset_ref("harness.graph.graph:Graph")).to(equal(True))
        expect(agent_tools_toolset_ref("tools.echo.echo:Echo")).to(equal(True))
        expect(agent_tools_toolset_ref("cdd_guidance.practices.bdd.bdd:Bdd")).to(equal(False))
        expect(agent_tools_toolset_ref("cdd_guidance.builders.create_agent_toolset.create_agent_toolset:CreateAgentToolset")).to(
            equal(False)
        )
        expect(agent_tools_toolset_ref("harness.guidance.guidance:Guidance")).to(equal(False))
        expect(agent_tools_toolset_ref("harness.diagnostics.guidance_diagnostics:GuidanceDiagnostics")).to(
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
        expect(host.checkout_server.tools).to(have_key("agent-tools-diagnostics.agent_tools_diagnostics"))

    with it("should treat agent_tools_diagnostics as kind tool for MCP enrollment"):
        tool = AgentToolsDiagnostics().tools["agent_tools_diagnostics"]
        expect(tool.kind).to(equal("tool"))

    with it("should never publish nested diagnostics tools as workspace probe targets"):
        tree = Path(tempfile.mkdtemp())
        try:
            installer = _installer(
                tree,
                [
                    "repo.push_commit",
                    "agent-tools-diagnostics.agent_tools_diagnostics",
                    "guidance-diagnostics.guidance_diagnostics",
                ],
                toolset_items=["space.repo.repo:Repo"],
            )
            scoped = AgentToolsProbe(installer, mcp_host=_host_of(_REPO_TOOLSET, _AGENT_TOOLS_DIAGNOSTICS_REF)).published
            expect(scoped).to(contain("repo.push_commit"))
            expect(scoped).not_to(contain("agent-tools-diagnostics.agent_tools_diagnostics"))
            expect(scoped).not_to(contain("guidance-diagnostics.guidance_diagnostics"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

    with it("should list repo.push_commit in published workspace MCP names"):
        tree = Path(tempfile.mkdtemp())
        try:
            installer = _installer(
                tree,
                ["repo.push_commit", "bdd-behavior", "cdd.ping"],
                toolset_items=["space.repo.repo:Repo"],
            )
            scoped = AgentToolsProbe(installer, mcp_host=_host_of(_REPO_TOOLSET)).published
            expect(scoped).to(equal(["repo.push_commit"]))
            expect(scoped).not_to(contain("bdd-behavior"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

    with it("should write agent_tools with ping and invoke sections"):
        tree = Path(tempfile.mkdtemp())
        try:
            installer = _installer(
                tree,
                ["repo.push_commit", "bdd-behavior", "cdd.ping"],
                toolset_items=["space.repo.repo:Repo"],
            )
            report = AgentToolsProbe(installer, mcp_host=_host_of(_REPO_TOOLSET)).run()
            expect("green" in report.split("\n")[0]).to(equal(True))
            data = json.loads((tree / "diagnostics.json").read_text(encoding="utf-8"))
            section = data[AGENT_TOOLS_PROBE_SECTION]
            expect("ping" in section).to(equal(True))
            expect("invoke" in section).to(equal(True))
            names = [item["mcp"] for item in section["ping"]["items"]]
            expect(names).to(contain("repo.push_commit"))
        finally:
            shutil.rmtree(tree, ignore_errors=True)

    with context("with a tool that does not answer within the probe's time limit"):
        with before.each:
            self.tree = Path(tempfile.mkdtemp())
            installer = _installer(self.tree, ["call-outcomes.close_month"], toolset_items=[_CALL_OUTCOMES])
            self.limit = agent_tools_probe._DISPATCH_SECONDS
            agent_tools_probe._DISPATCH_SECONDS = 0.02
            started = time.perf_counter()
            self.report = AgentToolsProbe(installer, mcp_host=_host_of(_CALL_OUTCOMES)).invoke()
            self.elapsed = time.perf_counter() - started

        with after.each:
            agent_tools_probe._DISPATCH_SECONDS = self.limit
            shutil.rmtree(self.tree, ignore_errors=True)

        with it("should answer before the tool finishes"):
            expect(self.elapsed < MONTH_END_SECONDS).to(equal(True))

        with it("should report the probe red"):
            expect(self.report.split("\n")[0]).to(equal("!red"))

with description("the agent tools diagnostics tool's description"):
    with before.all:
        self.description = AgentToolsDiagnostics().tools["agent_tools_diagnostics"].docstring

    with it("should name every operation the light phase only pings"):
        expect([name for name in agent_tools_probe._SKIP_INVOKE if name not in self.description]).to(equal([]))

    with it("should name every tool prefix the light phase leaves alone"):
        expect([prefix for prefix in agent_tools_probe._INVOKE_SKIP_PREFIXES if prefix not in self.description]).to(equal([]))

    with it("should name no one IDE's folder as where the report is"):
        expect(".cursor/diagnostics.json" in self.description).to(equal(False))
