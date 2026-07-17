# Sketch — Maintainer Behavior

Narrative for maintainers of the sketch module itself. AI reading this file: this describes how the module is structured and where design authority lives.

## What lives here

- `sketch.py` — the `Sketcher` toolset with three tools (`find_template`, `save_sketch`, `list_sketches`) and one standalone action (`sketch_session`).
- `_decorator.py` — the `@sketch` decorator (module-level function).
- `sketch.md` — the canonical philosophy / behavior contract read by AI at runtime.
- `sketch-template.md` — the default terse-indent template used when tiered discovery finds nothing else.
- `__init__.py` — public exports (`sketch`, `Sketcher`).

## Design authority

The design record for sketching lives at `ooad/.context/rethinking-fidelity-and-process.md`. That file is the source of truth for:

- Why sketch is an activity, not a fidelity tier.
- Why the primitive is chainable actions via decorators (`@sketch`, `@grill_context`, `@action`).
- Why decorators fire in declaration order top-down.
- Why template discovery is tiered (session → convention → default).
- Why `@sketch` annotates the action, not the class.

Do not re-derive that reasoning here — read the design record.

## v1 status

| Component | Status |
|---|---|
| `Sketcher` toolset (tools + action) | Implemented. Callable standalone via `python -m tools manifest sketch.sketch:Sketcher`. |
| `@sketch` decorator markers (`_sketch_wrapped`, `_sketch_preamble`) | Implemented. |
| `@sketch` auto-integration with `ActionExpander` (prepend preamble to expanded prose) | **Deferred slice** — see design record. Requires a small extension to `action/action.py`. |
| BDD specs for `Sketcher` and `@sketch` | **Deferred slice** — follow the `ooad/ooad_spec.py` pattern once the decorator integration lands. |

## How to consume today

Two paths:

1. **Explicit invocation of Sketcher** — any agent or human can invoke `Sketcher.sketch_session(slug, fidelity, agent_dir)` before running the formal generator. This works today with zero framework changes.

2. **Decorator marker for future auto-composition** — apply `@sketch` on top of `@action` on a generator method. The marker is set today; framework composition will pick it up in the deferred slice.

## When to change the default template

Change `sketch-template.md` only when the terse-indent notation itself is being revised. Domain-specific templates should live at `{agent_dir}/sketch-template.*` (per the convention tier of discovery) — do not modify the default to cater to one domain.
