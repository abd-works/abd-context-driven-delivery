"""Format expanded @agent_instructions prose for harness run responses."""
from __future__ import annotations

from typing import Any, Callable

from agent_tools.agent_tools import AgentTool


def format_agent_instructions(
    *,
    instructions: str,
    tools: list[str],
    toolset_path: str,
    context: dict[str, Any],
    tool_callables: dict[str, Callable[..., Any]],
) -> str:
    """Turn domain-expanded instructions into agent-facing runbook text (CLI channel)."""
    lines: list[str] = []
    if instructions.strip():
        lines.append(instructions.strip())
        lines.append("")
    lines.extend(_yaml_block(toolset_path, context))
    lines.append("Run: python -m harness run -")
    lines.append("")
    lines.extend(_available_tools_lines(tools, tool_callables))
    lines.extend(_tool_hint_lines(tools, tool_callables))
    return "\n\n".join(line for line in lines if line != "").strip()


def _yaml_block(toolset_path: str, context: dict[str, Any]) -> list[str]:
    lines = [
        "Every tool call uses this shape - set `tool` and `arguments`, pipe to CLI:",
        "",
        "```yaml",
        f"toolset: {toolset_path}",
        "context:",
    ]
    for key, value in context.items():
        lines.append(f"  {key}: {value}")
    lines += ["tool: <tool name>", "arguments:", "  <if needed>", "```", ""]
    return lines


def _available_tools_lines(
    tools: list[str],
    tool_callables: dict[str, Callable[..., Any]],
) -> list[str]:
    unique = list(dict.fromkeys(tools))
    if not unique:
        return []
    lines = [
        "Before following the suggested flow, display the tools made available to this chat "
        "in your user-visible reply — each tool name and what it is for. "
        "Do not only follow them silently or rediscover them by remanifesting.",
        "",
        "Tools made available:",
    ]
    for tool_name in unique:
        tool_func = tool_callables.get(tool_name)
        purpose = ""
        if tool_func is not None:
            text = (AgentTool.from_callable(tool_func).description or "").strip()
            purpose = text.splitlines()[0].strip() if text else ""
        lines.append(f"- {tool_name} — {purpose}" if purpose else f"- {tool_name}")
    lines.append("")
    return lines


def _tool_hint_lines(
    tools: list[str],
    tool_callables: dict[str, Callable[..., Any]],
) -> list[str]:
    lines = ["Suggested flow (repeat and reorder as the story needs):", ""]
    for index, tool_name in enumerate(tools, start=1):
        lines.append(f"{index}. tool: {tool_name}")
        tool_func = tool_callables.get(tool_name)
        if tool_func is not None:
            parameters = AgentTool.from_callable(tool_func).parameters
            if parameters:
                lines.append("   arguments:")
                hints = "\n     ".join(f"{name}: <value>" for name in parameters)
                lines.append(f"     {hints}")
        lines.append("")
    return lines
