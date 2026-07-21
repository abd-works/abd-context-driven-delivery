"""@focus decorator — marks an @action or @instruction to bind a focus group.

On @action: ActionExpander appends {module_dir}/{focus}/{filter_value}.md to prose.
On @instruction: sets group/filter_key so Instruction.ref resolves the same file
(or folder layout) via AssetLocator — e.g. @focus(focus="fidelities") on rules.

The filter_key is derived automatically from the group name:
  "fidelities" → "fidelity"   (ies → y)
  "formats"    → "format"     (trailing s stripped)
  "modes"      → "mode"

Raises TypeError when applied to a target that is neither @action nor @instruction.
"""
from __future__ import annotations

from typing import Any, Callable


def _default_filter_key(focus_group: str) -> str:
    if focus_group.endswith("ies"):
        return focus_group[:-3] + "y"
    return focus_group.rstrip("s")


def focus(
    func: Callable[..., Any] | None = None,
    *,
    focus: str,
    filter_key: str | None = None,
) -> Callable[..., Any]:
    """Bind a focus group to an @action or @instruction method.

    filter_value = getattr(instance, filter_key); content lives at
    {module_dir}/{focus}/{filter_value}.md (or under that path for folders).
    """
    resolved_key = filter_key or _default_filter_key(focus)

    def decorate(f: Callable[..., Any]) -> Callable[..., Any]:
        is_action = getattr(f, "_is_action", False)
        is_instruction = getattr(f, "_is_instruction_slot", False)
        if not is_action and not is_instruction:
            raise TypeError(
                f"@focus must decorate an @action or @instruction method; got {f.__name__!r} "
                f"which is neither. Apply @action or @instruction first, then @focus."
            )
        existing: list[tuple[str, str]] = list(getattr(f, "_focus_entries", []))
        f._focus_entries = existing + [(focus, resolved_key)]  # type: ignore[attr-defined]
        if is_instruction:
            f._instruction_group = focus  # type: ignore[attr-defined]
            f._instruction_filter_key = resolved_key  # type: ignore[attr-defined]
        return f

    if func is not None:
        return decorate(func)
    return decorate
