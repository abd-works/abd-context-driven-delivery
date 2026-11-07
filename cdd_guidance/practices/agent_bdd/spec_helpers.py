"""Shared helpers for agent BDD specs — expand/invoke on live toolsets, path layout, assertions.

Specs stay thin: construct or load a toolset, expand ``instructions[name]`` or
invoke ``operations[name]``, assert the result. Import from
``cdd_guidance.practices.agent_bdd.spec_helpers``; the steps that need the agent are on the block ``agent(...)`` yields.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from expects import be_true, equal, expect

from cdd_guidance.practices.agent_bdd.agent_bdd_common import (
    TOOL_RUN_TIMEOUT_SECONDS,
    RunResponse,
    ToolsetInvoke,
    invoke_run_request,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------


def repo_root_from(file: str | Path, *, parents: int = 2) -> Path:
    """Resolve the abd-context-driven-delivery root from a spec file path."""
    return Path(file).resolve().parents[parents]


def sessions_dir(spec_file: str | Path, *, folder: str = ".agent_bdd_sessions") -> Path:
    """Session JSON directory under .context/ in the spec's package."""
    return Path(spec_file).resolve().parent / ".context" / folder


CAR = "cdd_guidance.practices._examples.car.car:Car"
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
            "toolset": "cdd_guidance.actions._examples.car_story.car_story:CarStory",
            "action": "travelTo",
            "arguments": {
                "guidance": [car_tool_argument()],
                "destination": "town",
                "conditions": "dry",
            },
        },
        CAR_INSPECT.replace("\\", "/"): {
            "toolset": "cdd_guidance.actions._examples.car_story.car_story:CarStory",
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
    """Deploy the car skills into ``repo_root/.cursor``. The install also writes the user-level MCP entry and starts the
    cdd server, so both go to a throwaway home and ``~/.cdd`` that are removed afterwards."""
    from harness.installation.installer import Installer
    from harness.agent_tools.agent_tools import AgentToolSet
    from harness.mcp.spec_support import SpecServer, UserHome

    car = AgentToolSet.instantiate(CAR)
    car_story = AgentToolSet.instantiate("cdd_guidance.actions._examples.car_story.car_story:CarStory")
    home, server = UserHome(), SpecServer()
    home.enter()
    server.install()
    try:
        Installer("Cursor", path=repo_root / ".cursor", repo=repo_root_from(__file__, parents=3)).install([car, car_story], replace=False)
    finally:
        server.stop()
        home.leave()


def ensure_invoke_staged(repo_root: Path) -> None:
    key = str(repo_root.resolve())
    if key in _staged_roots:
        return
    stage_invoke_commands(repo_root)
    _staged_roots.add(key)


# ---------------------------------------------------------------------------
# In-process toolset invoke
# ---------------------------------------------------------------------------



def invoke_toolset(
    *,
    project: Path,
    toolset: str,
    tool: str | None = None,
    action: str | None = None,
    context: Mapping[str, Any] | None = None,
    arguments: Mapping[str, Any] | None = None,
) -> RunResponse:
    """Invoke one tool or action in-process on project, for specs that run no agent."""
    return ToolsetInvoke.for_toolset(
        toolset, project, tool=tool, action=action, context=context, arguments=arguments
    ).response()


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
    timeout_seconds: int = TOOL_RUN_TIMEOUT_SECONDS,
) -> RunResponse:
    """Invoke a deployed skill path using its fixture run-request mapping, on repo_root."""
    request = invoke_request_for_path(command, repo_root=repo_root)
    merged = dict(request)
    if context:
        merged_context = dict(merged.get("context") or {})
        merged_context.update(dict(context))
        merged["context"] = merged_context
    if arguments:
        merged["arguments"] = dict(arguments)
    return invoke_run_request(merged, repo_root, timeout_seconds)


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
