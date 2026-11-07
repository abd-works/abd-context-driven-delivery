"""Workspace MCP probe for ``/agent-tools-diagnostics``.

Uses the **live** cdd server's ``McpHost``, the one every chat talks to — ping, light invoke, and
heavy invoke (``cdd-diagnostic`` fixtures) all call ``host.dispatch`` on that host. Tests
without a live host use ``AgentToolsProbe.run_standalone`` (one-off host, not used in MCP).
"""
from __future__ import annotations

import concurrent.futures
import inspect
import os
import sys
from pathlib import Path
from typing import Any

from harness.agent_tools.agent_tools import AgentToolSet
from harness.agent_tools.name import Name
from harness.agent_tools.cdd_diagnostic_bridge import probe_arguments_from_cdd_diagnostic
from harness.guidance.guidance_probe import GuidanceProbe, failure_text, instruction_result, probe_subsection

_HEAVY_INVOKE_PREFIXES = ("session.", "sessions.", "graph.")

_INVOKE_DISPATCH_TIMEOUT_SECONDS = 12.0
_INVOKE_SKIP_PREFIXES = (
    "session.",
    "sessions.",
    "graph.",
    "partition.",
    "catalog.",
    "repo.",
)

AGENT_TOOLS_PROBE_SECTION = "agent_tools"

AGENT_TOOLS_TOOLSET_PREFIXES = ("space.", "harness.", "tools.")
AGENT_TOOLS_TOOLSET_EXCLUDES = ("harness.guidance.", "harness.guidance_actions.")

_SKIP_INVOKE: dict[str, str] = {
    "repo.push_commit": "ping only (git)",
    "repo.close_branch": "ping only (git)",
    "repo.close_worktree": "ping only (git)",
    "repo.switch_branch": "ping only (git)",
    "repo.switch_worktree": "ping only (git)",
    "installer.install": "use /install shell",
    "installer.clean": "use /clean shell",
    "agent-tools-diagnostics.agent_tools_diagnostics": "nested diagnostics probe",
    "guidance-diagnostics.guidance_diagnostics": "nested guidance diagnostics probe",
}

_NEVER_PROBE: frozenset[str] = frozenset(
    {
        "agent-tools-diagnostics.agent_tools_diagnostics",
        "guidance-diagnostics.guidance_diagnostics",
    }
)


def _probe_progress(phase: str, mcp_name: str, detail: str) -> None:
    """Live trace on stderr only (stdout is MCP JSON-RPC). CDD_PROBE_QUIET=1 silences."""
    if os.environ.get("CDD_PROBE_QUIET", "0") == "1":
        return
    sys.stderr.write(f"[agent-tools] {phase} {mcp_name}: {detail}\n")
    sys.stderr.flush()


def agent_tools_toolset_ref(ref: str) -> bool:
    module = ref.split(":", 1)[0]
    if any(module.startswith(prefix) for prefix in AGENT_TOOLS_TOOLSET_EXCLUDES):
        return False
    return any(module.startswith(prefix) for prefix in AGENT_TOOLS_TOOLSET_PREFIXES)


def _slug_for_toolset_ref(ref: str) -> str:
    """Slug for install-log matching — no toolset ``__init__`` on the MCP worker thread."""
    toolset_cls = AgentToolSet._load(ref)
    return Name(getattr(toolset_cls, "domain_slug", None) or toolset_cls.__name__).kebab


class ProbeRequiresServingHost(RuntimeError):
    """Raised when diagnostics run outside the live CDD MCP host process."""


class AgentToolsProbe:
    """A probe of the workspace MCP tools one install deployed (space, harness, and tools): ping each, call the light
    ones with probe arguments, and call session and graph tools with ``cdd-diagnostic`` fixtures. Made for its
    Installer and the guidance slugs a tool needs as its ``guidance`` argument; results go under ``agent_tools`` in
    diagnostics.json."""

    def __init__(self, installer: Any, guidance: list[str] | None = None) -> None:
        self.installer = installer
        self.slugs = list(guidance or [])

    @property
    def toolset_refs(self) -> tuple[str, ...]:
        """The deployed space, harness, and tools toolsets; every such toolset in the repository before an install."""
        refs = [ref for ref in self.installer.installed_items("toolset") if agent_tools_toolset_ref(ref)]
        if refs:
            return tuple(refs)
        self.installer.ensure_import_path(self.installer.repo)
        return tuple(ref for ref in self.installer.collect_toolsets() if agent_tools_toolset_ref(ref))

    @property
    def published(self) -> list[str]:
        """The installed workspace MCP names, limited to those the live host serves when one is running."""
        from harness.mcp.mcp_server import serving_mcp_host

        installed = {name for name in self.installer.installed_items("mcp") if name != "cdd.ping"}
        slugs = {_slug_for_toolset_ref(ref) for ref in self.toolset_refs}
        allowed = {
            name
            for name in installed
            if name not in _NEVER_PROBE and any(name == slug or name.startswith(f"{slug}.") for slug in slugs)
        }
        live = serving_mcp_host()
        if live is None:
            return sorted(allowed)
        runtime = live._runtime
        return sorted({name for name in (*runtime._tools, *runtime._prompts) if name in allowed})

    @property
    def host(self) -> Any:
        """The live cdd server's host; diagnostics never start a second one inside the server."""
        from harness.mcp.mcp_server import serving_mcp_host

        live = serving_mcp_host()
        if live is None:
            raise ProbeRequiresServingHost(
                "Agent-tools diagnostics require serving_mcp_host() — invoke "
                "agent-tools-diagnostics.agent_tools_diagnostics on the CDD MCP "
                "host Cursor already runs, not a separate Python process."
            )
        return live

    def run(self) -> str:
        """Ping, invoke, and heavy invoke on the live MCP host; on a one-off host when no host is serving."""
        from harness.mcp.mcp_server import serving_mcp_host

        _probe_progress("run", "agent-tools-diagnostics", "start")
        if serving_mcp_host() is None:
            report = self.run_standalone()
            _probe_progress("run", "agent-tools-diagnostics", "done")
            return report
        self._prepare_workspace()
        report = self._all_phases(self.host)
        _probe_progress("run", "agent-tools-diagnostics", "done")
        return report

    def run_standalone(self) -> str:
        """Ping, invoke, and heavy invoke on a one-off in-process host (specs and scripts)."""
        from harness.mcp.mcp_server import McpHost

        self._prepare_workspace()
        self.installer.ensure_import_path(self.installer.repo)
        refs = tuple(self.installer.collect_toolsets())
        project = str(self.installer.path) if getattr(self.installer, "path", None) else str(self.installer.repo)
        host = McpHost.from_refs(refs, repo=str(self.installer.repo), project=project)
        host._mark_as_serving()
        try:
            return self._all_phases(host)
        finally:
            host._unbind_as_serving()

    def ping(self) -> str:
        published = self.published
        host = self.host
        _probe_progress("ping", f"{len(published)} tools", "start")
        probes: list[dict[str, Any]] = []
        for mcp_name in published:
            item = _probe_mcp_ping_host(host, mcp_name)
            probes.append(item)
            _probe_progress("ping", mcp_name, item.get("color", "done"))
        subsection = probe_subsection("ping", [], probes)
        self.installer.write_diagnostics_section(AGENT_TOOLS_PROBE_SECTION, {"ping": subsection})
        return f"green\n{subsection['report']}"

    def invoke(self, host: Any | None = None) -> str:
        published = set(self.published)
        probe_host = host if host is not None else self.host
        probes: list[dict[str, Any]] = []
        files = GuidanceProbe(self.installer, self.slugs)
        try:
            _probe_progress("invoke", f"{len(published)} enrolled", "start")
            for mcp_name in sorted(published):
                skip = _invoke_skip_reason(mcp_name)
                if skip:
                    _probe_progress("invoke", mcp_name, f"skip ({skip})")
                item = self.invoke_one(probe_host, mcp_name, files, phase="invoke")
                probes.append(item)
                if not skip:
                    _probe_progress("invoke", mcp_name, item.get("color", item.get("skipped", "done")))
        finally:
            files.cleanup()
        subsection = probe_subsection("invoke", self.slugs, probes)
        failures = [item for item in probes if item.get("color") == "red"]
        color = "red" if failures else "green"
        self.installer.write_diagnostics_section(
            AGENT_TOOLS_PROBE_SECTION,
            {
                "color": color,
                "scope": list(AGENT_TOOLS_TOOLSET_PREFIXES),
                "toolset_count": len(self.toolset_refs),
                "invoke": subsection,
            },
        )
        prefix = "!" if color == "red" else ""
        return f"{prefix}{color}\n{subsection['report']}"

    def heavy_invoke(self, host: Any) -> str:
        """Session/graph invokes using ``cdd-diagnostic`` workspace fixtures."""
        try:
            from cdd_diagnostic.workspace import WorkspaceFixtures  # noqa: F401
        except ImportError:
            subsection = probe_subsection(
                "heavy_invoke",
                [],
                [{"mcp": "cdd-diagnostic", "color": "yellow", "skipped": "pip install -e ../cdd-diagnostic"}],
            )
            self.installer.write_diagnostics_section(AGENT_TOOLS_PROBE_SECTION, {"heavy_invoke": subsection})
            return f"yellow\n{subsection['report']}"

        files = GuidanceProbe(self.installer, [])
        probes: list[dict[str, Any]] = []
        try:
            published = set(self.published)
            _probe_progress("heavy_invoke", "session/graph", "start")
            for mcp_name in sorted(published):
                if not any(mcp_name.startswith(prefix) for prefix in _HEAVY_INVOKE_PREFIXES):
                    continue
                if probe_arguments_from_cdd_diagnostic(mcp_name, self.installer.repo) is None:
                    _probe_progress("heavy_invoke", mcp_name, "skip (no fixture)")
                    probes.append({"mcp": mcp_name, "color": "yellow", "skipped": "no cdd-diagnostic fixture"})
                    continue
                item = self.invoke_one(host, mcp_name, files, phase="heavy_invoke")
                probes.append(item)
                _probe_progress("heavy_invoke", mcp_name, item.get("color", "done"))
            subsection = probe_subsection("heavy_invoke", [], probes)
            failures = [item for item in probes if item.get("color") == "red"]
            color = "red" if failures else "green"
            self.installer.write_diagnostics_section(
                AGENT_TOOLS_PROBE_SECTION,
                {"heavy_invoke": subsection, "color": color},
            )
            prefix = "!" if color == "red" else ""
            return f"{prefix}{color}\n{subsection['report']}"
        finally:
            files.cleanup()

    def invoke_one(
        self,
        host: Any,
        mcp_name: str,
        files: GuidanceProbe,
        *,
        phase: str = "invoke",
    ) -> dict[str, Any]:
        """Call one MCP operation on host with probe arguments; files makes, and later removes, any files they need."""
        skip = _invoke_skip_reason(mcp_name)
        if skip:
            return {"mcp": mcp_name, "color": "yellow", "skipped": skip}
        runtime = host._runtime
        resolved = runtime.resolve_call_name(mcp_name)
        if resolved not in runtime._tools and resolved not in runtime._prompts:
            return {"mcp": mcp_name, "color": "red", "failure": "not enrolled on host"}

        enrolled = runtime._tools.get(resolved) or runtime._prompts.get(resolved)
        member = enrolled.callable
        args, missing = files.arguments_for(mcp_name, member)
        if missing:
            extra, still_missing = self._workspace_arguments(mcp_name, member)
            args = {**args, **extra}
            missing = still_missing
        if missing:
            return {"mcp": mcp_name, "color": "red", "failure": "needs " + ", ".join(missing)}
        try:
            result = _dispatch_timed(host, mcp_name, args or None, phase=phase)
        except Exception as exc:
            _probe_progress(phase, mcp_name, failure_text(exc))
            return {"mcp": mcp_name, "color": "red", "failure": failure_text(exc)}
        item = instruction_result(mcp_name, result)
        if args.get("paths"):
            item["paths"] = args["paths"]
        return item

    def _all_phases(self, host: Any) -> str:
        return "\n\n".join((self.ping(), self.invoke(host), self.heavy_invoke(host)))

    def _prepare_workspace(self) -> None:
        """Make the ``cdd-diagnostic`` workspace fixtures when that package is present. No git clean or switch: that
        can block on locks, and repo MCP invokes use probe arguments only."""
        from harness.agent_tools.cdd_diagnostic_bridge import _ensure_cdd_diagnostic_path

        _probe_progress("clean", "repo", "skip (no git switch/clean in diagnostics)")
        _ensure_cdd_diagnostic_path()
        try:
            from cdd_diagnostic.workspace import WorkspaceFixtures
        except ImportError:
            return
        WorkspaceFixtures(self.installer.repo)

    def _workspace_arguments(self, mcp_name: str, member: Any) -> tuple[dict[str, Any], list[str]]:
        try:
            signature = inspect.signature(member)
        except (TypeError, ValueError):
            return {}, ["callable"]
        bridged = probe_arguments_from_cdd_diagnostic(mcp_name, self.installer.repo)
        if bridged is not None:
            return bridged
        repo_root = str(Path(self.installer.repo).resolve())
        param_names = _signature_parameter_names(signature)
        args = _builtin_workspace_probe_arguments(mcp_name, repo_root, param_names)
        missing = _missing_required_arguments(signature, args)
        if not missing and not args and not _missing_required_arguments(signature, {}):
            return {}, []
        return args, missing


def _invoke_skip_reason(mcp_name: str) -> str | None:
    if mcp_name in _SKIP_INVOKE:
        return _SKIP_INVOKE[mcp_name]
    for prefix in _INVOKE_SKIP_PREFIXES:
        if mcp_name.startswith(prefix):
            return "skipped for invoke (heavy or mutating)"
    return None


def _dispatch_timed(
    host: Any,
    mcp_name: str,
    arguments: dict[str, Any] | None,
    *,
    phase: str = "invoke",
) -> object:
    """Invoke with a hard timeout so diagnostics never hang on git or sub-agents."""
    _probe_progress(phase, mcp_name, f"call {arguments!r}"[:200])

    from harness.mcp.mcp_server import serving_mcp_host

    if phase == "ping" and serving_mcp_host() is not None:
        result = host.dispatch(mcp_name, arguments)
        _probe_progress(phase, mcp_name, "returned")
        return result

    def _call() -> object:
        return host.dispatch(mcp_name, arguments)

    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_call)
        try:
            result = future.result(timeout=_INVOKE_DISPATCH_TIMEOUT_SECONDS)
        except concurrent.futures.TimeoutError:
            _probe_progress(phase, mcp_name, f"timeout ({_INVOKE_DISPATCH_TIMEOUT_SECONDS}s)")
            raise TimeoutError(
                f"{mcp_name} did not finish within {_INVOKE_DISPATCH_TIMEOUT_SECONDS}s"
            ) from None
    _probe_progress(phase, mcp_name, "returned")
    return result


def _probe_mcp_ping_host(host: Any, mcp_name: str) -> dict[str, Any]:
    try:
        result = _dispatch_timed(host, mcp_name, {"ping": True}, phase="ping")
    except KeyError:
        return {"mcp": mcp_name, "color": "red", "failure": "not enrolled on host"}
    except Exception as exc:
        return {"mcp": mcp_name, "color": "red", "failure": failure_text(exc)}
    if isinstance(result, dict) and result.get("ping") == "pong":
        return {"mcp": mcp_name, "color": "green", "preview": "pong"}
    return {
        "mcp": mcp_name,
        "color": "red",
        "failure": f"unexpected ping response: {result!r}"[:400],
    }


def _signature_parameter_names(signature: inspect.Signature) -> set[str]:
    return {
        name
        for name, param in signature.parameters.items()
        if name not in {"self", "cls"}
        and param.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    }


def _missing_required_arguments(
    signature: inspect.Signature,
    args: dict[str, Any],
) -> list[str]:
    required = [
        name
        for name, param in signature.parameters.items()
        if name not in {"self", "cls"}
        and param.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        and param.default is inspect.Parameter.empty
    ]
    return [name for name in required if name not in args]


def _builtin_workspace_probe_arguments(
    mcp_name: str,
    repo_root: str,
    param_names: set[str],
) -> dict[str, Any]:
    if mcp_name == "sessions.switch":
        return {"name": "_cdd_mcp_probe"}
    if mcp_name.startswith("echo.") and "body" in param_names:
        return {"body": "agent-tools-diagnostics probe"}
    return {}
