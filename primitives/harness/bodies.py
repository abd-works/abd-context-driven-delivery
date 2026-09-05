# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: do not remanifest — slash/skill is the catalog. Pipe the fence to stdin; python -m tools run -. Follow response.instructions only. Do not author behavior from this Python source.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Bodies for generated harness files — ContextToolBody, ContextToolFidelityBody, ActionBody, UtilityBody, FormatBody, Resolve."""

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
    "Pipe the fence to stdin from the repo root. Do not write a request file. "
    "Do not remanifest — this skill is the catalog. "
    "Follow response.instructions only.\n"
)


def _invoke_block(
    toolset: str,
    *,
    action: str | None = None,
    tool: str | None = None,
    fidelity: str | None = None,
    constructor_context: dict[str, str] | None = None,
) -> str:
    """Filled invoke fence plus one ``tools.ps1 run -`` (manifest-alone path, #45)."""
    lines = ["```yaml", f"toolset: {toolset}"]
    ctx: dict[str, str] = dict(constructor_context or {})
    if fidelity:
        ctx["fidelity"] = fidelity
    if ctx:
        lines.append("context:")
        for k, v in ctx.items():
            lines.append(f"  {k}: {v}")
    if tool:
        lines.append(f"tool: {tool}")
    elif action:
        lines.append(f"action: {action}")
    lines.append("```")
    lines.append(".\\tools.ps1 run -")
    return "\n".join(lines) + "\n"


def resolve_text(
    source: str,
    toolset: str,
    *,
    kind: str = "action",
    fidelities: list[str] | tuple[str, ...] = (),
    actions: list[str] | tuple[str, ...] = (),
    context_tools: list[str] | tuple[str, ...] = (),
    invoke: str = "action",
    constructor_context: dict[str, str] | None = None,
    extended: bool = False,
) -> str:
    """Resolve rules plus the CLI. Action and guidance bodies get opposite confirm lines.

    ``extended`` swaps both confirm lines to consider a straight prompt passed
    versus ct; ``ct_fidelity`` is the extended composite kind for
    ``{context_tool}-{fidelity}`` commands — the guidance confirm line, then
    the CLI fence with the fidelity pinned and ``action: generate``, never a
    fidelity AskQuestion.
    """
    toolset = toolset.strip() or "the in-scope context tool"
    cc = constructor_context or {}
    if kind == "fidelity":
        return _CATALOG_LINE + _invoke_block(toolset, action="generate", fidelity=source, constructor_context=cc)
    if kind in {"utility", "format"}:
        if kind == "format":
            return "through the tools cli\n\n" + _CATALOG_LINE + _invoke_block(toolset, constructor_context=cc)
        member = source.strip()
        if invoke == "tool" and member:
            return (
                "through the tools cli\n\n"
                + _CATALOG_LINE
                + _invoke_block(toolset, tool=member, constructor_context=cc)
            )
        if invoke == "action" and member:
            return (
                "through the tools cli\n\n"
                + _CATALOG_LINE
                + _invoke_block(toolset, action=member, constructor_context=cc)
            )
        return "through the tools cli\n\n" + _CATALOG_LINE + _invoke_block(toolset, constructor_context=cc)
    if kind in {"guidance", "ct_fidelity"}:
        if actions:
            action_ask = (
                "AskQuestion constrained to these actions: "
                + " | ".join(actions)
            )
        else:
            action_ask = "AskQuestion constrained to the available actions for this context tool"
        if extended or kind == "ct_fidelity":
            taken = (
                "With a straight prompt passed, take the action from the prompt. "
                "If you took an action from the context versus being given a straight prompt, "
                f"confirm the use of the context. {action_ask}.\n"
            )
        else:
            taken = (
                "If you took an action from the context versus being given an explicit one, "
                f"confirm the use of the context. {action_ask}.\n"
            )
    else:
        tool_options = list(context_tools) + ["use existing context only"]
        tool_ask = (
            "AskQuestion constrained to the context tools: " + " | ".join(tool_options)
        )
        if extended:
            taken = (
                "With a straight prompt passed, run this action on the context in general. "
                "If you took a context tool from the context and not a straight prompt, "
                f"confirm the use of the context. {tool_ask}.\n"
            )
        else:
            taken = (
                "If you took guidance from the context and not a tool, "
                f"confirm the use of the context. {tool_ask}.\n"
            )
    if kind == "ct_fidelity":
        return (
            taken
            + "Then run:\n"
            + _CATALOG_LINE
            + _invoke_block(toolset, action="generate", fidelity=source, constructor_context=cc)
        )
    if kind == "guidance":
        if fidelities:
            skill_options = " | ".join(f"{source}-{fidelity}" for fidelity in fidelities)
            fidelity_ask = (
                f"AskQuestion constrained to these fidelity skills: {skill_options}. "
                f"Run the chosen skill (@{source}-<fidelity>); do not pipe YAML from this skill.\n"
            )
        else:
            fidelity_ask = (
                "AskQuestion to choose the appropriate fidelity skill for this context tool. "
                "Run the chosen skill; do not pipe YAML from this skill.\n"
            )
        return taken + fidelity_ask
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
            + _invoke_block(toolset, tool=source, constructor_context=cc)
        )
    action = source if kind == "action" else None
    return (
        taken
        + fidelity_ask
        + "Then run:\n"
        + _CATALOG_LINE
        + _invoke_block(toolset, action=action, constructor_context=cc)
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
        extended: bool = False,
    ) -> "ContextToolBody":
        text = (
            f"# {name}\n\n"
            f"{overview}\n\n"
            f"{resolve_text(name, toolset, kind='guidance', fidelities=fidelities, actions=actions, extended=extended)}"
        )
        return cls(text)

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class ContextToolFidelityBody(ContextToolBody):
    """Composite — all context-tool content plus the pinned fidelity.

    One ``{context_tool}-{fidelity}`` command: guidance expanded through
    the same ActionExpander as the YAML contract, projected to this fidelity,
    with higher-abstraction fidelity commands referenced rather than inlined.
    """

    @classmethod
    def from_source(
        cls,
        *,
        overview: str,
        toolset: str,
        guidance: str = "",
        instructions: str = "",
        fidelities: list[str] | tuple[str, ...] = (),
        actions: list[str] | tuple[str, ...] = (),
        fidelity: str = "",
        constructor_context: dict[str, str] | None = None,
    ) -> "ContextToolFidelityBody":
        content = (instructions or "").strip()
        if not content:
            candidate = (guidance or "").strip()
            content = candidate if candidate and candidate != "guidance" else overview
        tool_name = _context_tool_name(toolset)
        previous: list[str] = []
        if fidelity in fidelities:
            previous = list(fidelities[: fidelities.index(fidelity)])
        references = ""
        if previous:
            mentions = "\n".join(
                f"@{tool_name}-{higher}" for higher in reversed(previous)
            )
            references = (
                "\n\nUse higher-level fidelity guidance only when required information "
                "is missing. Reference these commands with `@`; do not inline "
                f"their content:\n{mentions}"
            )
        text = (
            f"# {tool_name}-{fidelity}\n\n"
            f"Use {tool_name} guidance at `{fidelity}` fidelity only."
            f"{references}\n\n"
            f"{content}"
        )
        return cls(text)


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
        constructor_context: dict[str, str] | None = None,
        extended: bool = False,
    ) -> "ActionBody":
        if kind == "fidelity":
            tool_name = _context_tool_name(toolset)
            text = (
                f"Run the action on {tool_name} at {name} fidelity through the tools cli\n\n"
                f"{resolve_text(name, toolset, kind=kind, fidelities=fidelities, constructor_context=constructor_context, extended=extended)}"
            )
            return cls(text)
        member = (operation or name).strip()
        text = (
            f"# {name}\n\n"
            "Run this action for any provided context tools, or on the context in general.\n\n"
            f"{class_string}\n\n"
            f"{operation_instructions}\n\n"
            f"{resolve_text(member, toolset, kind=kind, fidelities=fidelities, context_tools=context_tools, invoke=invoke, constructor_context=constructor_context, extended=extended)}"
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
        invoke: str = "tool",
        operation: str = "",
        constructor_context: dict[str, str] | None = None,
    ) -> "UtilityBody":
        parts = [part for part in (class_string.strip(), operation_instructions.strip()) if part]
        if constructor_context:
            missing = [k for k, v in constructor_context.items() if not v]
            if missing:
                parts.append(
                    f"Required context params with no value: {', '.join(missing)}. "
                    "AskQuestion to collect each missing value before running."
                )
        member = (operation or "").strip()
        text = (
            "\n\n".join(parts)
            + "\n\n"
            + resolve_text(member, toolset, kind="utility", invoke=invoke, constructor_context=constructor_context)
        )
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
