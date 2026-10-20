"""Workspace MCP probe for ``/agent-tools-diagnostics``.

Uses the **live** CDD stdio ``McpHost`` already running in Cursor — ping, light invoke, and
heavy invoke (``cdd-diagnostic`` fixtures) all call ``host.dispatch`` on that host. Tests
without a live host use ``probe_agent_tools_standalone`` (one-off host, not used in MCP).
"""
from __future__ import annotations

import concurrent.futures
import inspect
import os
import re
import sys
from pathlib import Path
from typing import Any

_HEAVY_INVOKE_PREFIXES = ("session.", "graph.")

_INVOKE_DISPATCH_TIMEOUT_SECONDS = 12.0
_INVOKE_SKIP_PREFIXES = (
    "session.",
    "graph.",
    "partition.",
    "catalog.",
    "repo.",
)

from harness.agent_tools.agent_tools import AgentToolSet, InstallDestination
from harness.guidance.guidance import (
    ActionProbeSession,
    _failure_text,
    _instruction_result,
    fill_probe_arguments,
    installed_channel_items,
    probe_subsection,
)
from harness.mcp.mcp_server import McpOperationDefinition, McpPrompt

AGENT_TOOLS_PROBE_SECTION = "agent_tools"

AGENT_TOOLS_TOOLSET_PREFIXES = ("space.", "harness.", "tools.")
AGENT_TOOLS_TOOLSET_EXCLUDES = ("harness.guidance.", "harness.guidance_actions.")

_SKIP_INVOKE: dict[str, str] = {
    "repo.push": "ping only (git)",
    "repo.close_branch": "ping only (git)",
    "repo.close_worktree": "ping only (git)",
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


def _toolset_module(ref: str) -> str:
    return ref.split(":", 1)[0]


def agent_tools_toolset_ref(ref: str) -> bool:
    module = _toolset_module(ref)
    if any(module.startswith(prefix) for prefix in AGENT_TOOLS_TOOLSET_EXCLUDES):
        return False
    return any(module.startswith(prefix) for prefix in AGENT_TOOLS_TOOLSET_PREFIXES)


def agent_tools_toolset_refs(installer: Any) -> tuple[str, ...]:
    installed = installed_channel_items(installer, "toolset")
    refs = [ref for ref in installed if agent_tools_toolset_ref(ref)]
    if refs:
        return tuple(refs)
    installer.ensure_import_path(installer.repo)
    return tuple(ref for ref in installer.collect_toolsets() if agent_tools_toolset_ref(ref))


def _slug_for_toolset_ref(ref: str) -> str:
    """Slug for install-log matching — no toolset ``__init__`` on the MCP worker thread."""
    toolset_cls = AgentToolSet._load(ref)
    domain = getattr(toolset_cls, "domain_slug", None)
    if domain:
        return str(domain).replace("_", "-")
    name = toolset_cls.__name__
    return re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", name).lower()


class ProbeRequiresServingHost(RuntimeError):
    """Raised when diagnostics run outside the live CDD MCP host process."""


def probe_mcp_host(installer: Any) -> Any:
    from harness.mcp.mcp_server import serving_mcp_host

    live = serving_mcp_host()
    if live is None:
        raise ProbeRequiresServingHost(
            "Agent-tools diagnostics require serving_mcp_host() — invoke "
            "agent-tools-diagnostics.agent_tools_diagnostics on the CDD MCP "
            "host Cursor already runs, not a separate Python process."
        )
    return live


def _allowed_workspace_mcp_names(installer: Any) -> set[str]:
    installed = {n for n in installed_channel_items(installer, "mcp") if n != "cdd.ping"}
    slugs = {_slug_for_toolset_ref(ref) for ref in agent_tools_toolset_refs(installer)}
    return {
        name
        for name in installed
        if name not in _NEVER_PROBE
        and any(name == slug or name.startswith(f"{slug}.") for slug in slugs)
    }


def published_agent_tools_mcp(installer: Any) -> list[str]:
    """Install-log workspace MCP names (space / harness / tools), intersected with the live host."""
    from harness.mcp.mcp_server import serving_mcp_host

    allowed = _allowed_workspace_mcp_names(installer)
    live = serving_mcp_host()
    if live is not None:
        runtime = live._runtime
        names = [
            name
            for name in (*runtime._tools, *runtime._prompts)
            if name in allowed
        ]
        return sorted(set(names))
    return sorted(allowed)


def probe_agent_tools_ping(installer: Any) -> str:
    published = published_agent_tools_mcp(installer)
    host = probe_mcp_host(installer)
    _probe_progress("ping", f"{len(published)} tools", "start")
    probes: list[dict[str, Any]] = []
    for mcp_name in published:
        item = _probe_mcp_ping_host(host, mcp_name)
        probes.append(item)
        _probe_progress("ping", mcp_name, item.get("color", "done"))
    subsection = probe_subsection("ping", [], probes)
    installer.write_diagnostics_section(AGENT_TOOLS_PROBE_SECTION, {"ping": subsection})
    return f"green\n{subsection['report']}"


def probe_agent_tools_invoke(
    installer: Any,
    guidance: list[str] | None = None,
    *,
    host: Any | None = None,
) -> str:
    slugs = list(guidance or [])
    published = set(published_agent_tools_mcp(installer))
    probe_host = host if host is not None else probe_mcp_host(installer)
    probes: list[dict[str, Any]] = []
    session = ActionProbeSession(installer)
    try:
        _probe_progress("invoke", f"{len(published)} enrolled", "start")
        for mcp_name in sorted(published):
            skip = _invoke_skip_reason(mcp_name)
            if skip:
                _probe_progress("invoke", mcp_name, f"skip ({skip})")
            item = _probe_mcp_invoke_host(
                probe_host, mcp_name, slugs, session, installer, phase="invoke"
            )
            probes.append(item)
            if not skip:
                _probe_progress("invoke", mcp_name, item.get("color", item.get("skipped", "done")))
    finally:
        session.cleanup()
    subsection = probe_subsection("invoke", slugs, probes)
    failures = [item for item in probes if item.get("color") == "red"]
    color = "red" if failures else "green"
    installer.write_diagnostics_section(
        AGENT_TOOLS_PROBE_SECTION,
        {
            "color": color,
            "scope": list(AGENT_TOOLS_TOOLSET_PREFIXES),
            "toolset_count": len(agent_tools_toolset_refs(installer)),
            "invoke": subsection,
        },
    )
    prefix = "!" if color == "red" else ""
    return f"{prefix}{color}\n{subsection['report']}"


def probe_agent_tools_heavy_invoke(installer: Any, host: Any) -> str:
    """Session/graph invokes using ``cdd-diagnostic`` workspace fixtures."""
    from harness.agent_tools.cdd_diagnostic_bridge import probe_arguments_from_cdd_diagnostic

    try:
        from cdd_diagnostic.workspace import WorkspaceFixtures
    except ImportError:
        subsection = probe_subsection(
            "heavy_invoke",
            [],
            [
                {
                    "mcp": "cdd-diagnostic",
                    "color": "yellow",
                    "skipped": "pip install -e ../cdd-diagnostic",
                }
            ],
        )
        installer.write_diagnostics_section(AGENT_TOOLS_PROBE_SECTION, {"heavy_invoke": subsection})
        return f"yellow\n{subsection['report']}"

    session = ActionProbeSession(installer)
    probes: list[dict[str, Any]] = []
    try:
        published = set(published_agent_tools_mcp(installer))
        _probe_progress("heavy_invoke", "session/graph", "start")
        for mcp_name in sorted(published):
            if not any(mcp_name.startswith(prefix) for prefix in _HEAVY_INVOKE_PREFIXES):
                continue
            if probe_arguments_from_cdd_diagnostic(mcp_name, installer.repo) is None:
                _probe_progress("heavy_invoke", mcp_name, "skip (no fixture)")
                probes.append(
                    {
                        "mcp": mcp_name,
                        "color": "yellow",
                        "skipped": "no cdd-diagnostic fixture",
                    }
                )
                continue
            item = _probe_mcp_invoke_host(
                host, mcp_name, [], session, installer, phase="heavy_invoke"
            )
            probes.append(item)
            _probe_progress("heavy_invoke", mcp_name, item.get("color", "done"))
        subsection = probe_subsection("heavy_invoke", [], probes)
        failures = [item for item in probes if item.get("color") == "red"]
        color = "red" if failures else "green"
        installer.write_diagnostics_section(
            AGENT_TOOLS_PROBE_SECTION,
            {"heavy_invoke": subsection, "color": color},
        )
        prefix = "!" if color == "red" else ""
        return f"{prefix}{color}\n{subsection['report']}"
    finally:
        session.cleanup()


def _standalone_host(installer: Any) -> Any:
    from harness.mcp.mcp_server import McpHost

    installer.ensure_import_path(installer.repo)
    refs = tuple(installer.collect_toolsets())
    project = str(installer.path) if getattr(installer, "path", None) else str(installer.repo)
    return McpHost.from_refs(refs, repo=str(installer.repo), project=project)


def probe_agent_tools_standalone(installer: Any, guidance: list[str] | None = None) -> str:
    """Ping + light + heavy invoke on a one-off in-process host (tests)."""
    _clean_repo_before_probe(installer)
    host = _standalone_host(installer)
    host._bind_as_serving()
    try:
        return "\n\n".join(
            (
                probe_agent_tools_ping(installer),
                probe_agent_tools_invoke(installer, guidance, host=host),
                probe_agent_tools_heavy_invoke(installer, host),
            )
        )
    finally:
        host._unbind_as_serving()


def probe_agent_tools(installer: Any, guidance: list[str] | None = None) -> str:
    """Ping + invoke + heavy on the live MCP host (no second host load)."""
    from harness.mcp.mcp_server import serving_mcp_host

    slugs = list(guidance or [])
    _probe_progress("run", "agent-tools-diagnostics", "start")
    if serving_mcp_host() is None:
        report = probe_agent_tools_standalone(installer, slugs)
        _probe_progress("run", "agent-tools-diagnostics", "done")
        return report
    _clean_repo_before_probe(installer)
    host = probe_mcp_host(installer)
    report = "\n\n".join(
        (
            probe_agent_tools_ping(installer),
            probe_agent_tools_invoke(installer, slugs, host=host),
            probe_agent_tools_heavy_invoke(installer, host),
        )
    )
    _probe_progress("run", "agent-tools-diagnostics", "done")
    return report


def probe_workspace_toolset(
    ref: str,
    published: set[str],
    slugs: list[str],
    session: ActionProbeSession,
    installer: Any,
) -> list[dict[str, Any]]:
    try:
        toolset = AgentToolSet.instantiate(ref)
    except Exception as exc:
        return [{"toolset": ref, "color": "red", "failure": _failure_text(exc)}]
    probes: list[dict[str, Any]] = []
    for tool in toolset.tools_for(InstallDestination.MCP):
        operation = McpOperationDefinition.from_tool(tool)
        if operation.mcp_name not in published:
            continue
        if not agent_tools_toolset_ref(ref):
            continue
        skip = _SKIP_INVOKE.get(operation.mcp_name)
        if skip:
            probes.append({"mcp": operation.mcp_name, "color": "yellow", "skipped": skip})
            continue
        probes.append(
            _probe_workspace_action(toolset, tool.name, operation, slugs, session, installer)
        )
    return probes


def _workspace_fixtures(installer: Any) -> Any | None:
    from harness.agent_tools.cdd_diagnostic_bridge import _ensure_cdd_diagnostic_path

    _ensure_cdd_diagnostic_path()
    try:
        from cdd_diagnostic.workspace import WorkspaceFixtures
    except ImportError:
        return None
    return WorkspaceFixtures(installer.repo)


def _clean_repo_before_probe(installer: Any) -> Any | None:
    """No git clean/switch — that can block on locks; repo MCP invoke uses probe args only."""
    _probe_progress("clean", "repo", "skip (no git switch/clean in diagnostics)")
    return _workspace_fixtures(installer)


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
        return {"mcp": mcp_name, "color": "red", "failure": _failure_text(exc)}
    if isinstance(result, dict) and result.get("ping") == "pong":
        return {"mcp": mcp_name, "color": "green", "preview": "pong"}
    return {
        "mcp": mcp_name,
        "color": "red",
        "failure": f"unexpected ping response: {result!r}"[:400],
    }


def _probe_mcp_invoke_host(
    host: Any,
    mcp_name: str,
    slugs: list[str],
    session: ActionProbeSession,
    installer: Any,
    *,
    phase: str = "invoke",
) -> dict[str, Any]:
    skip = _invoke_skip_reason(mcp_name)
    if skip:
        return {"mcp": mcp_name, "color": "yellow", "skipped": skip}
    runtime = host._runtime
    resolved = runtime.resolve_call_name(mcp_name)
    if resolved not in runtime._tools and resolved not in runtime._prompts:
        return {"mcp": mcp_name, "color": "red", "failure": "not enrolled on host"}

    enrolled = runtime._tools.get(resolved) or runtime._prompts.get(resolved)
    member = enrolled.callable
    args, missing = fill_probe_arguments(mcp_name, member, slugs, session)
    if missing:
        extra, still_missing = fill_workspace_probe_arguments(
            mcp_name, member, installer, session
        )
        args = {**args, **extra}
        missing = still_missing
    if missing:
        return {
            "mcp": mcp_name,
            "color": "red",
            "failure": "needs " + ", ".join(missing),
        }
    try:
        result = _dispatch_timed(host, mcp_name, args or None, phase=phase)
    except Exception as exc:
        _probe_progress(phase, mcp_name, _failure_text(exc))
        return {"mcp": mcp_name, "color": "red", "failure": _failure_text(exc)}
    item = _instruction_result(mcp_name, result)
    if args.get("paths"):
        item["paths"] = args["paths"]
    return item


def _probe_workspace_action(
    toolset: Any,
    name: str,
    operation: McpOperationDefinition,
    slugs: list[str],
    session: ActionProbeSession,
    installer: Any,
) -> dict[str, Any]:
    member = getattr(toolset, name)
    args, missing = fill_probe_arguments(operation.mcp_name, member, slugs, session)
    if missing:
        extra, still_missing = fill_workspace_probe_arguments(
            operation.mcp_name, member, installer, session
        )
        args = {**args, **extra}
        missing = still_missing
    if missing:
        return {
            "mcp": operation.mcp_name,
            "color": "red",
            "failure": "needs " + ", ".join(missing),
        }
    try:
        if operation.kind == "prompt":
            result = McpPrompt(operation).invoke(args)
        elif args:
            result = member(**args)
        else:
            result = member()
    except Exception as exc:
        return {"mcp": operation.mcp_name, "color": "red", "failure": _failure_text(exc)}
    item = _instruction_result(operation.mcp_name, result)
    if args.get("paths"):
        item["paths"] = args["paths"]
    return item


def fill_workspace_probe_arguments(
    mcp_name: str,
    member: Any,
    installer: Any,
    session: ActionProbeSession,
) -> tuple[dict[str, Any], list[str]]:
    try:
        signature = inspect.signature(member)
    except (TypeError, ValueError):
        return {}, ["callable"]
    param_names = {
        name
        for name, param in signature.parameters.items()
        if name != "self" and name != "cls"
        and param.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
    }
    root = str(Path(installer.repo).resolve())
    from harness.agent_tools.cdd_diagnostic_bridge import probe_arguments_from_cdd_diagnostic

    bridged = probe_arguments_from_cdd_diagnostic(mcp_name, installer.repo)
    if bridged is not None:
        return bridged

    args: dict[str, Any] = {}

    if mcp_name in {"session.session", "session.open_named"}:
        args = {"name": "_cdd_mcp_probe", "repo_path": root}
    elif mcp_name == "session.new":
        args = {"name": "_cdd_mcp_probe", "workpath": root, "repo_path": root}
    elif mcp_name == "session.switch":
        args = {"name": "_cdd_mcp_probe", "repo_path": root}
    elif mcp_name in {
        "repo.branch",
        "repo.worktree",
        "repo.new_worktree",
        "repo.switch_worktree",
    }:
        args = {"name": "_cdd-diagnostic-probe"}
    elif mcp_name == "repo.new_branch":
        args = {"name": "_cdd-diagnostic-probe", "switch": False}
    elif mcp_name == "repo.switch_branch":
        args = {"name": "main"}
    elif mcp_name.startswith("echo-instructions.") and "body" in param_names:
        args = {"body": "agent-tools-diagnostics probe"}
    required = [
        name
        for name, param in signature.parameters.items()
        if name not in {"self", "cls"}
        and param.kind
        not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
        and param.default is inspect.Parameter.empty
    ]
    missing = [name for name in required if name not in args]
    if not missing and not args and not required:
        return {}, []
    return args, missing
