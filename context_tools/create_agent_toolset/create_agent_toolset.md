# Instructions

Generate an **AgentToolSet** — a class decorated with `@agent_toolset` whose `@agent_tool` methods run as Python and whose `@agent_instructions` methods are recipes: string literals plus `tools(...)` / `instructions(...)` wrappers that expand to prose and a deferred tool list. Recipe bodies are never executed.

Scaffold from **`templates/`**. **Matching by** the canonical example under **`examples/car/`**.

Every generate ends with **validate**.

---
# Contexts

## Matching by the car example

- **`matching-by`** — Shape the new toolset after **`examples/car/`**. Same decorator marks, `recipe` first parameter on `@agent_instructions`, `tools(...)` / `instructions(...)` wrappers, ordinary `@property` state — not a parallel layout, not `@resource`, not bare `self.tool()` in a recipe.

## Recipes are walked, not run

- **`actions-are-recipes`** — `@agent_instructions` bodies are parsed with `ast`. First parameter is **`recipe`**. Reach the toolset with `recipe.toolset`. Wrap member calls in `tools(...)` (defer to agent invoke) or `instructions(...)` (expand nested recipe inline). Prose is string literals in the body. No conditionals-as-control-flow that the walker cannot see; no assignments except `recipe.toolset.mode`.

## Tools do the real work

- **`tools-do-work`** — Computation, I/O, and external calls live in `@agent_tool` methods with normal Python `self`. Recipes orchestrate; tools execute.

## Docstrings are agent instructions

- **`docstrings-as-instructions`** — The method docstring and extra string literals in the body become agent-visible instructions. Write them as commands.
- **`describe-what-things-do`** — Instructions state what a thing **does**. If a boundary matters, phrase the positive action that enforces it.

## Keep recipes thin

- **`keep-actions-thin`** — One `@agent_instructions` method per high-level orchestration goal. The `return` is a human-readable result; use `{{parameter}}` / `{{self.attr}}` for injected values.

## Observable state is ordinary properties

- **`resources-describe-state`** — Expose observable state as `@property`. Do not mark members `@resource`. Cross-call state lives on the live toolset instance.

---
# Generate

1. Read § Contexts and **`examples/car/`** — matching by that shape.
2. Scaffold from **`templates/`**.
3. Fill every `{Placeholder}` — class name, constructor params, tools, recipe(s), return statement.
4. Place the generated file in the domain folder that owns the toolset.
5. Run **validate**.
