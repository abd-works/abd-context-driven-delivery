"""Shared helpers for agent BDD specs — expand/invoke on live toolsets, path layout, assertions.

Specs stay thin: construct or load a toolset, expand ``instructions[name]`` or
invoke ``operations[name]``, assert the result. Import from
``agent_bdd.spec_helpers`` (or re-exports on ``agent_bdd``).
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from expects import be_true, equal, expect

from agent_bdd.agent_bdd_common import RunResponse, invoke_run_request

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def repo_root_from(file: str | Path, *, parents: int = 2) -> Path:
    """Resolve the abd-context-driven-delivery root from a spec file path."""
    return Path(file).resolve().parents[parents]


def sessions_dir(spec_file: str | Path, *, folder: str = ".agent_bdd_sessions") -> Path:
    """Session JSON directory under .context/ in the spec's package."""
    return Path(spec_file).resolve().parent / ".context" / folder


CAR = "practices.car.car:Car"
CAR_CTX = {
    "fidelity": "road_story",
    "make": "Dodge",
    "model": "Charger",
    "year": 1969,
    "personality": "General Lee",
}
CAR_SKILL = ".cursor/skills/context_tools/car/car/SKILL.md"
CAR_ROAD_STORY = ".cursor/skills/context_tools/car/car-road-story/SKILL.md"
TRAVEL_TO = ".cursor/skills/actions/travel-to/SKILL.md"
CAR_START = ".cursor/skills/context_tools/car/car-start/SKILL.md"
CAR_INSPECT = ".cursor/skills/actions/car-inspect/SKILL.md"
_staged_roots: set[str] = set()


def car_tool_argument() -> dict:
    return {"toolset": CAR, "context": dict(CAR_CTX)}


def invoke_request_for_path(command: str | Path, *, repo_root: Path) -> dict:
    path = Path(command)
    key = str(path.as_posix()).replace("\\", "/")
    if not path.is_file():
        candidate = (repo_root / path).resolve()
        key = str(candidate.relative_to(repo_root.resolve()).as_posix()).replace("\\", "/")
    mapping = {
        CAR_ROAD_STORY.replace("\\", "/"): {
            "toolset": CAR,
            "action": "generate",
            "context": dict(CAR_CTX),
        },
        CAR_START.replace("\\", "/"): {
            "toolset": CAR,
            "tool": "start",
            "context": dict(CAR_CTX),
        },
        TRAVEL_TO.replace("\\", "/"): {
            "toolset": "actions.examples.car_story.car_story:CarStory",
            "action": "travelTo",
            "arguments": {
                "guidance": [car_tool_argument()],
                "destination": "town",
                "conditions": "dry",
            },
        },
        CAR_INSPECT.replace("\\", "/"): {
            "toolset": "actions.examples.car_story.car_story:CarStory",
            "action": "inspect_trip",
            "arguments": {
                "guidance": [car_tool_argument()],
                "plan": "Night run to Atlanta.",
            },
        },
    }
    if key not in mapping:
        raise KeyError(f"No invoke mapping for deployed path {key!r}")
    return dict(mapping[key])


def stage_invoke_commands(repo_root: Path) -> None:
    from installation.installer import Installer
    from harness.agent_tools.agent_tools import AgentToolSet

    car = AgentToolSet.instantiate(CAR)
    car_story = AgentToolSet.instantiate("actions.examples.car_story.car_story:CarStory")
    Installer("Cursor", path=repo_root / ".cursor").install([car, car_story])


def ensure_invoke_staged(repo_root: Path) -> None:
    key = str(repo_root.resolve())
    if key in _staged_roots:
        return
    stage_invoke_commands(repo_root)
    _staged_roots.add(key)


# ---------------------------------------------------------------------------
# In-process toolset invoke
# ---------------------------------------------------------------------------


def build_run_request(
    *,
    toolset: str,
    tool: str | None = None,
    action: str | None = None,
    context: Mapping[str, Any] | None = None,
    arguments: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a spec run-request mapping."""
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
    return payload


def invoke_toolset(
    *,
    toolset: str,
    tool: str | None = None,
    action: str | None = None,
    context: Mapping[str, Any] | None = None,
    arguments: Mapping[str, Any] | None = None,
) -> RunResponse:
    """Invoke one tool or action in-process for specs."""
    return invoke_run_request(
        build_run_request(
            toolset=toolset,
            tool=tool,
            action=action,
            context=context,
            arguments=arguments,
        )
    )


def command_path(repo_root: Path, command: str | Path) -> Path:
    """Resolve a deployed slash/skill path under ``.cursor/``."""
    path = Path(command)
    if path.is_file():
        return path.resolve()
    resolved = (repo_root / path).resolve()
    if resolved.is_file():
        return resolved
    legacy = (repo_root / ".cursor" / "commands" / f"{path.name}").resolve()
    if legacy.is_file():
        return legacy
    raise FileNotFoundError(f"Deployed command not found: {resolved}")


def run_skill(
    command: str | Path,
    *,
    repo_root: Path,
    context: Mapping[str, Any] | None = None,
    arguments: Mapping[str, Any] | None = None,
    timeout_seconds: int = 180,
    require_agent_shell: bool = False,
) -> RunResponse:
    """Invoke a deployed skill path using its fixture run-request mapping."""
    _ = timeout_seconds, require_agent_shell
    request = invoke_request_for_path(command, repo_root=repo_root)
    merged = dict(request)
    if context:
        merged_context = dict(merged.get("context") or {})
        merged_context.update(dict(context))
        merged["context"] = merged_context
    if arguments:
        merged["arguments"] = dict(arguments)
    return invoke_run_request(merged)


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
    """Invoke one toolset member in-process."""
    _ = timeout_seconds, require_agent_shell
    return invoke_toolset(
        toolset=toolset,
        tool=tool,
        action=action,
        context=context,
        arguments=arguments,
    )


def read_workspace(path: str, *, timeout_seconds: int = 120) -> Any:
    """Prime the agent by reading a workspace-relative file."""
    from agent_bdd import instruct

    return instruct(f"Read {path} from the workspace.", timeout_seconds=timeout_seconds)


def follow_instructions(prompt: str, *, timeout_seconds: int = 300) -> Any:
    """Natural-language step after an action returned ``response.instructions``."""
    from agent_bdd import instruct

    return instruct(prompt, timeout_seconds=timeout_seconds)


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
