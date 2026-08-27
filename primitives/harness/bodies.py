# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Bodies for generated harness files — ContextToolBody, ActionBody, UtilityBody, FormatBody, Resolve."""

from __future__ import annotations

from dataclasses import dataclass


def _context_tool_name(toolset: str) -> str:
    ref = toolset.strip()
    if ":" in ref:
        module, class_name = ref.rsplit(":", 1)
        slug = module.rsplit(".", 1)[-1]
        return slug or class_name
    return ref or "the in-scope context tool"


_CATALOG_LINE = (
    "Pipe the fence to stdin. Do not write a request file. "
    "Do not remanifest — this skill is the catalog.\n"
)


def _invoke_block(
    toolset: str, *, action: str | None = None, fidelity: str | None = None
) -> str:
    """Filled invoke fence plus one ``run -`` (1b, 1c, 4c, 5a)."""
    lines = ["```yaml", f"toolset: {toolset}"]
    if fidelity:
        lines.append("context:")
        lines.append(f"  fidelity: {fidelity}")
    if action:
        lines.append(f"action: {action}")
    lines.append("```")
    lines.append("python -m tools run -")
    return "\n".join(lines) + "\n"


def resolve_text(
    source: str,
    toolset: str,
    *,
    kind: str = "action",
    fidelities: list[str] | tuple[str, ...] = (),
    actions: list[str] | tuple[str, ...] = (),
    context_tools: list[str] | tuple[str, ...] = (),
) -> str:
    """Resolve rules plus the CLI. Action and guidance bodies get opposite confirm lines."""
    toolset = toolset.strip() or "the in-scope context tool"
    if kind == "fidelity":
        return _CATALOG_LINE + _invoke_block(toolset, action="generate", fidelity=source)
    if kind in {"utility", "format"}:
        action = None if kind == "format" else source
        return "through the tools cli\n\n" + _CATALOG_LINE + _invoke_block(toolset, action=action)
    if kind == "guidance":
        if actions:
            action_ask = (
                "AskQuestion constrained to the actions in context_tools/actions: "
                + " | ".join(actions)
            )
        else:
            action_ask = "AskQuestion constrained to the actions in context_tools/actions"
        taken = (
            "If you took an action from the context versus being given an explicit one, "
            f"confirm the use of the context. {action_ask}.\n"
        )
    else:
        tool_options = list(context_tools) + ["use existing context only"]
        tool_ask = (
            "AskQuestion constrained to the context tools: " + " | ".join(tool_options)
        )
        taken = (
            "If you took guidance from the context and not a tool, "
            f"confirm the use of the context. {tool_ask}.\n"
        )
    fidelity_ask = (
        "If the fidelity does not belong to the in-scope tool or has not been provided, "
        "guess the correct fidelity and confirm with AskQuestion constrained to the other fidelities"
    )
    if fidelities:
        fidelity_ask += ": " + " | ".join(fidelities)
    fidelity_ask += ".\n"
    if kind == "action" and invoke == "tool":
        return (
            taken
            + fidelity_ask
            + "Then run:\n"
            + _CATALOG_LINE
            + _invoke_block(toolset, tool=source)
        )
    action = source if kind == "action" else None
    return (
        taken
        + fidelity_ask
        + "Then run:\n"
        + _CATALOG_LINE
        + _invoke_block(toolset, action=action)
    )


@dataclass(frozen=True)
class ContextToolBody:
    text: str

    @classmethod
    def from_source(
        cls,
        *,
        name: str,
        overview: str,
        toolset: str,
        fidelities: list[str] | tuple[str, ...] = (),
        actions: list[str] | tuple[str, ...] = (),
    ) -> "ContextToolBody":
        text = (
            f"# {name}\n\n"
            f"{overview}\n\n"
            f"{resolve_text(name, toolset, kind='guidance', fidelities=fidelities, actions=actions)}"
        )
        return cls(text)

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class ActionBody:
    text: str

    @classmethod
    def from_source(
        cls,
        *,
        name: str,
        class_string: str,
        operation_instructions: str,
        toolset: str,
        kind: str = "action",
        fidelities: list[str] | tuple[str, ...] = (),
        context_tools: list[str] | tuple[str, ...] = (),
        invoke: str = "action",
        operation: str = "",
    ) -> "ActionBody":
        if kind == "fidelity":
            tool_name = _context_tool_name(toolset)
            text = (
                f"Run the action on {tool_name} at {name} fidelity through the tools cli\n\n"
                f"{resolve_text(name, toolset, kind=kind, fidelities=fidelities)}"
            )
            return cls(text)
        member = (operation or name).strip()
        text = (
            f"# {name}\n\n"
            "Run this action for any provided context tools, or on the context in general.\n\n"
            f"{class_string}\n\n"
            f"{operation_instructions}\n\n"
            f"{resolve_text(member, toolset, kind=kind, fidelities=fidelities, context_tools=context_tools, invoke=invoke)}"
        )
        return cls(text)

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class UtilityBody:
    text: str

    @classmethod
    def from_source(
        cls,
        *,
        name: str,
        class_string: str,
        operation_instructions: str,
        toolset: str,
    ) -> "UtilityBody":
        parts = [part for part in (class_string.strip(), operation_instructions.strip()) if part]
        text = "\n\n".join(parts) + "\n\n" + resolve_text(name, toolset, kind="utility")
        return cls(text)

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class FormatBody:
    text: str

    @classmethod
    def from_source(cls, *, format: str) -> "FormatBody":
        text = (
            f"# {format}\n\n"
            f"Run the context tool / actions using the following format: {format}.\n"
            "Used mostly with generate and render.\n"
            "Do not set a fidelity from this prompt.\n\n"
            f"{resolve_text(format, 'the in-scope context tool', kind='format')}"
        )
        return cls(text)

    def __str__(self) -> str:
        return self.text
