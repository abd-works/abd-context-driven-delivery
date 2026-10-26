---
name: builders-create-agent-toolset
description: >-
  # Overview
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
---

overview

Use MCP tool: `create-agent-toolset.instructions()`
