# focus

## Purpose

Provides the `@focus` decorator, which binds a focus group to an `@action` or `@instruction` method. On `@action`, the ActionExpander appends the focus file's content to the action's prose. On `@instruction`, it sets the group and filter_key so the slot resolves the matching asset file via AssetLocator.

## Seam

`focus(func=None, *, focus: str, filter_key: str | None = None) -> Callable` — public decorator factory importable from the `focus` package. Supports both direct application (`@focus(focus="fidelities")`) and single-argument call (`focus(fn, focus="fidelities")`).

## Constraint

Callers must apply `@action` or `@instruction` before `@focus`; applying `@focus` to a plain function raises `TypeError`.

## Public API

- `focus` — decorator factory (module-level function, public surface)
- `_default_filter_key` — derives a singular filter key from a plural group name (module-level, used by `focus` and by tests)

## Dependencies

- `primitives.actions.action` — `@action` sets `_is_action = True` on the wrapped callable
- `primitives.instructions.instructions` — `@instruction` sets `_is_instruction_slot = True`
