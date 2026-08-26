# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""Bodies for generated harness files — ContextToolBody, ActionBody, FormatBody, Resolve."""

from __future__ import annotations

from dataclasses import dataclass


def resolve_text(source: str, toolset: str) -> str:
    """Resolve rules plus the CLI. Same block in every body kind."""
    toolset = toolset.strip() or "the in-scope context tool"
    return (
        "An action does not require a context tool.\n"
        "A context tool does not require an action.\n"
        "If you took qualitative guidance or an action from the context, confirm.\n"
        "If the fidelity does not belong to the in-scope tool, guess the correct fidelity and confirm.\n"
        f"If you cannot get guidance and cannot get the action, AskQuestion constrained to this source: {source}.\n"
        "Then run:\n"
        f"python -m tools manifest {toolset}\n"
        "python -m tools run _req.yaml\n"
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
        class_string: str,
        guidance: str,
        toolset: str,
    ) -> "ContextToolBody":
        text = (
            f"# {name}\n\n"
            f"{overview}\n\n"
            f"{class_string}\n\n"
            "Guidance:\n"
            f"{guidance}\n\n"
            f"{resolve_text(name, toolset)}"
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
    ) -> "ActionBody":
        text = (
            f"# {name}\n\n"
            "Run this action for any provided context tools, or on the context in general.\n\n"
            f"{class_string}\n\n"
            f"{operation_instructions}\n\n"
            f"{resolve_text(name, toolset)}"
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
            f"{resolve_text(format, 'the in-scope context tool')}"
        )
        return cls(text)

    def __str__(self) -> str:
        return self.text
