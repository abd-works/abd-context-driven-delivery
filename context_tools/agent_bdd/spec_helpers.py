"""Shared helpers for agent BDD specs — YAML run prompts, path layout, assertions.

Specs stay thin: build request YAML, call harness free functions, assert response fields.
Import from ``agent_bdd.spec_helpers`` (or re-exports on ``agent_bdd``).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml
from expects import be_true, equal, expect

from agent_bdd.agent_bdd_common import RunResponse, looks_like_tools_run_output

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def repo_root_from(file: str | Path, *, parents: int = 2) -> Path:
    """Resolve the abd-context-driven-delivery root from a spec file path."""
    return Path(file).resolve().parents[parents]


def sessions_dir(spec_file: str | Path, *, folder: str = ".agent_bdd_sessions") -> Path:
    """Session JSON directory under .context/ in the spec's package."""
    return Path(spec_file).resolve().parent / ".context" / folder


# ---------------------------------------------------------------------------
# tools run YAML + prompts
# ---------------------------------------------------------------------------


def dump_run_yaml(
    *,
    toolset: str,
    tool: str | None = None,
    action: str | None = None,
    context: Mapping[str, Any] | None = None,
    arguments: Mapping[str, Any] | None = None,
) -> str:
    """Serialize a ``python -m tools run`` request body."""
    if (tool is None) == (action is None):
        raise ValueError("Provide exactly one of tool= or action=")
    payload: dict[str, Any] = {"toolset": toolset}
    if context:
        payload["context"] = dict(context)
    if action is not None:
        payload["action"] = action
    else:
        payload["tool"] = tool
    if arguments:
        payload["arguments"] = dict(arguments)
    return yaml.safe_dump(payload, sort_keys=False).rstrip() + "\n"


def tools_run_prompt(run_yaml: str) -> str:
    """Standard instruct_use_tool prompt: pipe YAML to ``.\\tools.ps1 run -``."""
    body = run_yaml.rstrip()
    return (
        "Using shell from the repo root, run exactly: .\\tools.ps1 run -\n"
        "Pipe this YAML on stdin:\n"
        f"{body}\n"
        "Return the complete fenced YAML stdout from the CLI. "
        "Do not remanifest. Do not write a request file."
    )


_COMMAND_FENCE_RE = re.compile(r"```yaml\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)


def command_path(repo_root: Path, command: str | Path) -> Path:
    """Resolve a workspace-relative ``.cursor/commands/*.md`` path."""
    path = Path(command)
    if path.is_file():
        return path.resolve()
    resolved = (repo_root / path).resolve()
    if not resolved.is_file():
        raise FileNotFoundError(f"Deployed command not found: {resolved}")
    return resolved


def command_fence_yaml(command: str | Path, *, repo_root: Path) -> str:
    """Return the exact ```yaml fence body from a deployed slash/skill command."""
    path = command_path(repo_root, command)
    match = _COMMAND_FENCE_RE.search(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"No ```yaml fence in {path}")
    return match.group(1).rstrip() + "\n"


def parse_command_fence(command: str | Path, *, repo_root: Path) -> dict[str, Any]:
    """Parse the invoke fence from a deployed ``.cursor/commands/*.md`` skill."""
    payload = yaml.safe_load(command_fence_yaml(command, repo_root=repo_root))
    if not isinstance(payload, dict):
        raise ValueError(f"Command fence must be a mapping: {command}")
    return payload


def run_yaml_from_command(
    command: str | Path,
    *,
    repo_root: Path,
    context: Mapping[str, Any] | None = None,
    arguments: Mapping[str, Any] | None = None,
) -> str:
    """Build stdin YAML from a skill fence, optionally merging context/arguments."""
    payload = dict(parse_command_fence(command, repo_root=repo_root))
    if context:
        merged = dict(payload.get("context") or {})
        merged.update(dict(context))
        payload["context"] = merged
    if arguments:
        payload["arguments"] = dict(arguments)
    return yaml.safe_dump(payload, sort_keys=False).rstrip() + "\n"


def tools_run_prompt_from_command(
    command: str | Path,
    *,
    repo_root: Path,
    context: Mapping[str, Any] | None = None,
    arguments: Mapping[str, Any] | None = None,
) -> str:
    """Build a tools-run prompt from the exact invoke fence in a deployed command."""
    run_yaml = run_yaml_from_command(
        command,
        repo_root=repo_root,
        context=context,
        arguments=arguments,
    )
    return tools_run_prompt(run_yaml)


def run_skill(
    command: str | Path,
    *,
    repo_root: Path,
    context: Mapping[str, Any] | None = None,
    arguments: Mapping[str, Any] | None = None,
    timeout_seconds: int = 180,
    require_agent_shell: bool = False,
) -> RunResponse:
    """Invoke using YAML from a deployed skill fence (call ``read_workspace`` first)."""
    from agent_bdd import instruct_use_tool

    prompt = tools_run_prompt_from_command(
        command,
        repo_root=repo_root,
        context=context,
        arguments=arguments,
    )
    return instruct_use_tool(
        prompt,
        timeout_seconds=timeout_seconds,
        require_agent_shell=require_agent_shell,
    )


def run_toolset(
    *,
    toolset: str,
    tool: str | None = None,
    action: str | None = None,
    context: Mapping[str, Any] | None = None,
    arguments: Mapping[str, Any] | None = None,
    timeout_seconds: int = 180,
    require_agent_shell: bool = False,
) -> RunResponse:
    """Build YAML, drive ``instruct_use_tool``, return the parsed ``RunResponse``."""
    run_yaml = dump_run_yaml(
        toolset=toolset,
        tool=tool,
        action=action,
        context=context,
        arguments=arguments,
    )
    from agent_bdd import instruct_use_tool

    return instruct_use_tool(
        tools_run_prompt(run_yaml),
        timeout_seconds=timeout_seconds,
        require_agent_shell=require_agent_shell,
    )


def expect_agent_invoked_shell(block: Any, *, agent_text: str = "") -> None:
    """Assert the agent ran shell tools.ps1/tools run — not harness replay or deferral."""
    from agent_bdd.agent_bdd_common import reject_agent_deferral

    reject_agent_deferral(agent_text)
    captures = tools_run_captures(block)
    expect(len(captures) >= 1).to(be_true)
    combined = combined_capture_text(captures).lower()
    expect("tools.ps1 run" in combined or "tools run" in combined).to(be_true)
    expect("tools manifest" not in combined).to(be_true)


def read_workspace(path: str, *, timeout_seconds: int = 120) -> Any:
    """Prime the agent by reading a workspace-relative file."""
    from agent_bdd import instruct

    return instruct(f"Read {path} from the workspace.", timeout_seconds=timeout_seconds)


def follow_instructions(prompt: str, *, timeout_seconds: int = 300) -> Any:
    """Natural-language step after an action returned ``response.instructions``."""
    from agent_bdd import instruct

    return instruct(prompt, timeout_seconds=timeout_seconds)


def manifest_command_from_header(source_path: str | Path) -> str:
    """Return the ``@toolset-manifest`` shell command from a toolset source file."""
    from tools.toolset_header import read_toolset_header

    path = Path(source_path)
    if not path.is_file():
        path = Path.cwd() / source_path
    command = read_toolset_header(path).manifest_command
    if not command:
        raise ValueError(f"No @toolset-manifest command in {path}")
    return command


def run_manifest_from_header(source_path: str, *, timeout_seconds: int = 300) -> Any:
    """Ask the agent to run the ``@toolset-manifest`` command at the top of a source file.

    Prefers shell-capture stdout when the agent summarizes instead of echoing CLI output.
    """
    from agent_bdd import _current, instruct
    from agent_bdd.agent_bdd_common import AgentResult

    command = manifest_command_from_header(source_path)
    result = instruct(
        f"Using shell, run exactly: {command}\n"
        "Return the complete manifest stdout (full fenced YAML; do not summarize).",
        timeout_seconds=timeout_seconds,
    )
    captures = getattr(_current(), "last_shell_captures", None) or []
    for capture in reversed(captures):
        output = (getattr(capture, "output", None) or "").strip()
        lowered = output.lower()
        if output and ("type:" in lowered or "signature:" in lowered):
            return AgentResult(
                exit_code=result.exit_code,
                text=output,
                stderr=result.stderr,
                elapsed_seconds=result.elapsed_seconds,
            )
    return result


# ---------------------------------------------------------------------------
# Response assertions
# ---------------------------------------------------------------------------


def expect_ok_action(
    response: RunResponse,
    action: str,
    *,
    require_instructions: bool = True,
) -> None:
    """Assert ``ok``, matching ``action``, and optionally non-empty instructions."""
    expect(response.ok).to(be_true)
    expect(response.action).to(equal(action))
    if require_instructions:
        expect(response.instructions is not None).to(be_true)


def expect_ok_tool(response: RunResponse, tool: str) -> None:
    """Assert ``ok`` and matching ``tool`` name."""
    expect(response.ok).to(be_true)
    expect(response.tool).to(equal(tool))


def expect_tools_include(response: RunResponse, names: Sequence[str]) -> None:
    """Assert every name appears on ``response.tools``."""
    tools = response.tools or []
    for name in names:
        expect(name in tools).to(be_true)


def expect_tools_exclude(response: RunResponse, names: Sequence[str]) -> None:
    """Assert none of the names appear on ``response.tools``."""
    tools = response.tools or []
    for name in names:
        expect(name in tools).not_to(be_true)


def expect_instructions_contain(
    response: RunResponse,
    *needles: str,
    case_insensitive: bool = True,
) -> None:
    """Assert every needle appears in ``response.instructions``."""
    text = str(response.instructions or "")
    haystack = text.lower() if case_insensitive else text
    for needle in needles:
        probe = needle.lower() if case_insensitive else needle
        expect(probe in haystack).to(be_true)


def expect_instructions_contain_any(
    response: RunResponse,
    *needles: str,
    case_insensitive: bool = True,
) -> None:
    """Assert at least one needle appears in ``response.instructions``."""
    text = str(response.instructions or "")
    haystack = text.lower() if case_insensitive else text
    matched = any(
        (n.lower() if case_insensitive else n) in haystack for n in needles
    )
    expect(matched).to(be_true)


# ---------------------------------------------------------------------------
# Shell captures (action-following specs)
# ---------------------------------------------------------------------------


def tools_run_captures(block: Any) -> list[Any]:
    """Filter ``session_shell_captures`` to tools-run commands or outputs."""
    captures = getattr(block, "session_shell_captures", None) or []
    return [
        capture
        for capture in captures
        if "tools run" in capture.command.lower()
        or "tools.ps1 run" in capture.command.lower()
        or looks_like_tools_run_output(capture.output)
    ]


def combined_capture_text(captures: Sequence[Any], *extras: str) -> str:
    """Join shell captures (and optional extra stdout) for substring asserts."""
    parts = [f"{c.command}\n{c.output}" for c in captures]
    parts.extend(extras)
    return "\n".join(parts)


def expect_capture_mentions(combined: str, *needles: str) -> None:
    """Assert each needle appears in combined capture/stdout text (case-insensitive)."""
    haystack = combined.lower()
    for needle in needles:
        expect(needle.lower() in haystack).to(be_true)


def generate_similar_prompt(pass_path: str | Path) -> str:
    """Ask the agent to generate something similar to the passing fixture."""
    location = Path(pass_path).as_posix()
    return (
        f"Read {location}. Generate a similar successful result — the same kind of "
        "artifact, close in shape and content, not a copy. Hold this generate for "
        "human review."
    )


def generate_similar_rubric(pass_path: str | Path) -> str:
    """AI-judge rubric: generated output is close to the passing fixture."""
    location = Path(pass_path).as_posix()
    return (
        f"The output is a similar successful result to {location}: same kind of "
        "artifact, close in shape and intent, not an unrelated rewrite."
    )


def generate_and_judge(
    pass_path: str | Path,
    rubric: str | None = None,
    *,
    timeout_seconds: int = 300,
) -> str:
    """Generate against the pass fixture, judge it, return the artifact for review.

    Must be called inside ``with agent(...)``.
    """
    from agent_bdd import ai_judge, follow_instructions

    artifact = follow_instructions(
        generate_similar_prompt(pass_path),
        timeout_seconds=timeout_seconds,
    ).text
    ai_judge(artifact, rubric or generate_similar_rubric(pass_path))
    return artifact


# ---------------------------------------------------------------------------
# Agent redesign (#55) — ChatAgent toolset prompts for agent BDD specs
# ---------------------------------------------------------------------------

CHAT_AGENT_TOOLSET = "agent.chat_agent:ChatAgent"


def init_temp_workspace(prefix: str = "agent_bdd_") -> Path:
    """Temp workspace directory for one agent BDD run."""
    import tempfile

    return Path(tempfile.mkdtemp(prefix=prefix))


def chat_agent_context(workspace: Path, session: str) -> dict[str, str]:
    return {
        "workspace": str(workspace).replace("\\", "/"),
        "session": session,
    }


def parse_json_log_kinds(result: str) -> list[str]:
    import json

    text = (result or "").strip()
    if not text:
        return []
    return json.loads(text)


def chat_agent_tool_prompt(
    tool: str,
    *,
    context: Mapping[str, Any],
    arguments: Mapping[str, Any] | None = None,
    toolset: str = CHAT_AGENT_TOOLSET,
) -> str:
    """Standard ``instruct_use_tool`` prompt for a ChatAgent phased tool."""
    return tools_run_prompt(
        dump_run_yaml(
            toolset=toolset,
            tool=tool,
            context=context,
            arguments=arguments or {},
        )
    )
