"""Workspace MCP probe for ``/agent-tools-diagnostics``.

The probe calls tools through an MCP host: the live cdd server's host that answers the diagnostics call, the one every
chat talks to, or, for specs and scripts, a one-off host in this process."""
from __future__ import annotations

import concurrent.futures
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from harness.diagnostics.probe_arguments import OperationArguments, ProbeArguments
from harness.diagnostics.probe_outcome import ProbeOutcome, ProbeSection, raised_by_a_bug
from harness.mcp.mcp_server import McpHost

if TYPE_CHECKING:
    from harness.installation.installer import Installer

AGENT_TOOLS_PROBE_SECTION = "agent_tools"
AGENT_TOOLS_TOOLSET_PREFIXES = ("space.", "harness.", "tools.")
# Guidance and its diagnostics are probed by the guidance probe.
AGENT_TOOLS_TOOLSET_EXCLUDES = ("harness.guidance.", "harness.guidance_actions.", "harness.diagnostics.guidance_diagnostics")
# How long one probe call may run; a call still running then is reported red and left to finish on its own.
_DISPATCH_SECONDS = 12.0
# Session and graph tools are called only with the ``cdd-diagnostic`` fixtures, in the heavy phase.
_HEAVY_INVOKE_PREFIXES = ("session.", "sessions.", "graph.")
_INVOKE_SKIP_PREFIXES = ("session.", "sessions.", "graph.", "partition.", "catalog.", "repo.")
_SKIP_INVOKE: dict[str, str] = {
    "repo.push_commit": "ping only (git)",
    "installer.install": "use /install shell",
    "installer.clean": "use /clean shell",
    "app.install": "ping only (npm install and build)",
    "chats.open": "ping only (opens the Claude app)",
}
# The diagnostics tools themselves: probing them would run the probe inside itself.
_NEVER_PROBE = frozenset({"agent-tools-diagnostics.agent_tools_diagnostics", "guidance-diagnostics.guidance_diagnostics"})


class ProbeCallTimedOut(TimeoutError):
    """A tool the probe called did not answer within the probe's time limit; it keeps running on its own."""

    def __init__(self, tool: str, seconds: float) -> None:
        super().__init__(f"{tool} did not finish within {seconds:g}s")
        self.tool = tool


class AgentToolsProbe:
    """A probe of the workspace MCP tools one install deployed (space, harness, and tools): ping each, call the light
    ones with probe arguments, and call session and graph tools with ``cdd-diagnostic`` fixtures. Made for its
    Installer, the guidance slugs a tool needs as its ``guidance`` argument, and the MCP host it calls through; every
    call works on the Installer's project, and results go under ``agent_tools`` in diagnostics.json. Without a host it
    stands up a one-off host over every toolset of the Installer's checkout."""

    def __init__(self, installer: Installer, guidance: list[str] | None = None, mcp_host: McpHost | None = None) -> None:
        self.installer = installer
        self.slugs = list(guidance or [])
        self._mcp_host = mcp_host

    @property
    def project(self) -> Path:
        """The project every probed call works on: the one whose install is probed."""
        return self.installer.repo

    @property
    def host(self) -> McpHost:
        """The host this probe calls through."""
        if self._mcp_host is None:
            refs = tuple(str(reference) for reference in self.installer.toolsets.references())
            self._mcp_host = McpHost.from_refs(refs, repo=str(self.installer.repo), project=str(self.installer.path))
        return self._mcp_host

    @property
    def toolset_refs(self) -> tuple[str, ...]:
        """The deployed space, harness, and tools toolsets; every such toolset in the repository before an install."""
        refs = [ref for ref in self.installer.diagnostics.installed_items("toolset") if self._covers(ref)]
        if refs:
            return tuple(refs)
        refs = (str(reference) for reference in self.installer.toolsets.references())
        return tuple(ref for ref in refs if self._covers(ref))

    def _covers(self, toolset_ref: str) -> bool:
        """True when the toolset is one this probe covers: a space, harness, or tools toolset other than guidance."""
        module = toolset_ref.split(":", 1)[0]
        if any(module.startswith(prefix) for prefix in AGENT_TOOLS_TOOLSET_EXCLUDES):
            return False
        return any(module.startswith(prefix) for prefix in AGENT_TOOLS_TOOLSET_PREFIXES)

    @property
    def published(self) -> list[str]:
        """The installed workspace MCP names the host publishes from the probed toolsets."""
        installed = set(self.installer.diagnostics.installed_items("mcp")) - _NEVER_PROBE
        server = self.host.checkout_toolsets
        refs = set(self.toolset_refs)
        served = {name: tool for name, tool in (*server.tools.items(), *server.prompts.items())}
        return sorted(name for name, tool in served.items() if name in installed and str(tool.toolset.reference) in refs)

    def run(self) -> str:
        """Ping, invoke, and heavy invoke, each phase written to diagnostics.json; the reply holds each phase's colour."""
        self._progress("run", "agent-tools-diagnostics", "start")
        report = "\n\n".join((self.ping(), self.invoke(), self.heavy_invoke()))
        self._progress("run", "agent-tools-diagnostics", "done")
        return report

    def ping(self) -> str:
        """Ping every published tool, and report as red each probed toolset the host skipped at start-up."""
        published = self.published
        self._progress("ping", f"{len(published)} tools", "start")
        outcomes = [self._ping_one(name) for name in published] + self._skipped_at_start()
        section = ProbeSection("ping", outcomes)
        self.installer.diagnostics.write_section(AGENT_TOOLS_PROBE_SECTION, {"ping": section.record})
        return section.reply

    def invoke(self) -> str:
        """Call each published tool the light phase does not skip, with arguments made for the probe."""
        arguments = ProbeArguments(self.installer.repo, self.slugs)
        try:
            outcomes = [self._invoke_one(name, arguments) for name in self.published]
        finally:
            arguments.cleanup()
        section = ProbeSection("invoke", outcomes, self.slugs)
        record = {"scope": list(AGENT_TOOLS_TOOLSET_PREFIXES), "toolset_count": len(self.toolset_refs), "invoke": section.record}
        self.installer.diagnostics.write_section(AGENT_TOOLS_PROBE_SECTION, record)
        return section.reply

    def heavy_invoke(self) -> str:
        """Call each session and graph tool with its ``cdd-diagnostic`` fixture; yellow without the package."""
        arguments = ProbeArguments(self.installer.repo, [])
        if not arguments.fixtures.is_installed:
            outcomes = [ProbeOutcome.from_skip("cdd-diagnostic", "pip install -e ../cdd-diagnostic")]
        else:
            arguments.fixtures.prepare()
            heavy = [name for name in self.published if name.startswith(_HEAVY_INVOKE_PREFIXES)]
            outcomes = [self._heavy_invoke_one(name, arguments) for name in heavy]
        section = ProbeSection("heavy_invoke", outcomes)
        self.installer.diagnostics.write_section(AGENT_TOOLS_PROBE_SECTION, {"heavy_invoke": section.record})
        return section.reply

    def _ping_one(self, mcp_name: str) -> ProbeOutcome:
        try:
            answer = self._answer(mcp_name, {"ping": True}, "ping")
        except Exception as failure:
            if raised_by_a_bug(failure):
                raise
            return ProbeOutcome.from_failure(mcp_name, failure)
        if answer == {"ping": "pong", "tool": mcp_name}:
            return ProbeOutcome(mcp_name, ProbeOutcome.GREEN, preview="pong")
        return ProbeOutcome.from_refusal(mcp_name, f"unexpected ping response: {answer!r}")

    def _skipped_at_start(self) -> list[ProbeOutcome]:
        """A probed toolset, or an installed tool, the host skipped when it started."""
        probed = {*self.toolset_refs, *self.installer.diagnostics.installed_items("mcp")}
        skipped = self.host.checkout_toolsets.skipped.as_data
        return [ProbeOutcome.from_refusal(item["tool"], f"skipped at start-up: {item['reason']}") for item in skipped if item["tool"] in probed]

    def _invoke_one(self, mcp_name: str, arguments: ProbeArguments) -> ProbeOutcome:
        skip = _SKIP_INVOKE.get(mcp_name) or ("skipped for invoke (heavy or mutating)" if mcp_name.startswith(_INVOKE_SKIP_PREFIXES) else "")
        if skip:
            self._progress("invoke", mcp_name, f"skip ({skip})")
            return ProbeOutcome.from_skip(mcp_name, skip)
        return self._invoked_with(mcp_name, arguments, "invoke")

    def _heavy_invoke_one(self, mcp_name: str, arguments: ProbeArguments) -> ProbeOutcome:
        fixture = arguments.fixtures.probe_arguments(mcp_name)
        if fixture is None:
            self._progress("heavy_invoke", mcp_name, "skip (no fixture)")
            return ProbeOutcome.from_skip(mcp_name, "no cdd-diagnostic fixture")
        return self._called_with(mcp_name, OperationArguments(*fixture), "heavy_invoke")

    def _invoked_with(self, mcp_name: str, arguments: ProbeArguments, phase: str) -> ProbeOutcome:
        tool = self.host.checkout_toolsets.enrolled(mcp_name)
        if tool is None:
            return ProbeOutcome.from_refusal(mcp_name, "not enrolled on host")
        return self._called_with(mcp_name, arguments.for_operation(mcp_name, tool.callable), phase)

    def _called_with(self, mcp_name: str, arguments: OperationArguments, phase: str) -> ProbeOutcome:
        if arguments.missing:
            return ProbeOutcome.from_refusal(mcp_name, "needs " + ", ".join(arguments.missing))
        try:
            answer = self._answer(mcp_name, arguments.values or None, phase)
        except Exception as failure:
            if raised_by_a_bug(failure):
                raise
            return ProbeOutcome.from_failure(mcp_name, failure)
        return ProbeOutcome.from_answer(mcp_name, answer).called_on(arguments.values.get("paths") or [])

    def _answer(self, mcp_name: str, values: dict[str, object] | None, phase: str) -> object:
        """The tool's answer through the host, waiting at most ``_DISPATCH_SECONDS``. The call runs on a thread of its
        own that the probe never waits for past the limit, so a tool that hangs cannot hang the diagnostics."""
        self._progress(phase, mcp_name, f"call {values!r}"[:200])
        pool = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        try:
            answer = pool.submit(self.host.dispatch, mcp_name, values, self.project).result(timeout=_DISPATCH_SECONDS)
        except concurrent.futures.TimeoutError:
            self._progress(phase, mcp_name, f"timeout ({_DISPATCH_SECONDS:g}s)")
            raise ProbeCallTimedOut(mcp_name, _DISPATCH_SECONDS) from None
        finally:
            pool.shutdown(wait=False, cancel_futures=True)
        self._progress(phase, mcp_name, "returned")
        return answer

    def _progress(self, phase: str, mcp_name: str, detail: str) -> None:
        """A live trace on stderr, since stdout carries MCP; ``CDD_PROBE_QUIET=1`` silences it."""
        if os.environ.get("CDD_PROBE_QUIET", "0") == "1":
            return
        sys.stderr.write(f"[agent-tools] {phase} {mcp_name}: {detail}\n")
        sys.stderr.flush()
