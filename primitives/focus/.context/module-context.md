# focus

## Purpose

Provides the `@focus` decorator, which binds a focus group to an `@action` or `@instruction` method. On `@action`, the ActionExpander appends the focus file's content to the action's prose. On `@instruction`, it sets the group and filter_key so the slot resolves the matching asset file via AssetLocator.

## Seam

`focus(func=None, *, focus: str, filter_key: str | None = None) -> Callable` — public decorator factory importable from the `focus` package. Supports both direct application (`@focus(focus="fidelities")`) and single-argument call (`focus(fn, focus="fidelities")`).

## Constraint

Callers must apply `@action` or `@instruction` before `@focus`; applying `@focus` to a plain function raises `TypeError`.

## Public API

- `focus` — decorator factory (module-level function, public surface)

## Dependencies

- `primitives.actions.action` — `@action` marks the wrapped callable for action expansion
- `primitives.instructions.instructions` — `@instruction` marks the wrapped callable as an instruction slot
