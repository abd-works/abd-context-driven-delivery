# @toolset-manifest python -m tools manifest context_tools.bdd.bdd:Bdd
# Agent reading this file: run line 1 manifest, then python -m tools run -. Follow response.instructions only.
# invoke-edit: action satisfy | toolset: context_tools.bdd.bdd:Bdd
# invoke-check: action validate | toolset: context_tools.bdd.bdd:Bdd
"""@focus decorator - marks an @agent_instructions or @instruction to bind a focus group.

On @agent_instructions: ActionExpander appends {module_dir}/{focus}/{filter_value}.md to prose.
On @instruction: sets group/filter_key so Instruction.ref resolves the same file
(or folder layout) via AssetLocator - e.g. @focus(focus="fidelities") on rules.

The filter_key is derived automatically from the group name:
  "fidelities" -> "fidelity"   (ies -> y)
  "formats"    -> "format"     (trailing s stripped)
  "modes"      -> "mode"

Raises TypeError when applied to a target that is neither @agent_instructions nor @instruction.
"""
from __future__ import annotations

from typing import Any, Callable


def _default_filter_key(focus_group: str) -> str:
    if focus_group.endswith("ies"):
        return focus_group[:-3] + "y"
    return focus_group.rstrip("s")


class _FocusBinder:
    """Applies focus-group metadata to a decorated @agent_instructions or @instruction method."""

    def __init__(self, group: str, filter_key: str) -> None:
        self._group = group
        self._filter_key = filter_key

    def bind(self, target: Callable[..., Any]) -> Callable[..., Any]:
        is_action = getattr(target, "_is_agent_instructions", False)
        is_instruction = getattr(target, "_is_instruction_slot", False)
        if not is_action and not is_instruction:
            raise TypeError(
                f"@focus must decorate an @agent_instructions or @instruction method; got {target.__name__!r} "
                f"which is neither. Apply @agent_instructions or @instruction first, then @focus."
            )
        existing: list[tuple[str, str]] = list(getattr(target, "_focus_entries", []))
        target._focus_entries = existing + [(self._group, self._filter_key)]  # type: ignore[attr-defined]
        if is_instruction:
            target._instruction_group = self._group  # type: ignore[attr-defined]
            target._instruction_filter_key = self._filter_key  # type: ignore[attr-defined]
        return target


def focus(
    func: Callable[..., Any] | None = None,
    *,
    focus: str,
    filter_key: str | None = None,
) -> Callable[..., Any]:
    """Bind a focus group to an @agent_instructions or @instruction method.

    filter_value = getattr(instance, filter_key); content lives at
    {module_dir}/{focus}/{filter_value}.md (or under that path for folders).
    """
    binder = _FocusBinder(focus, filter_key or _default_filter_key(focus))
    if func is not None:
        return binder.bind(func)
    return binder.bind
