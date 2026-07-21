# Instructions

Generate a **toolset with actions** — a `@toolset` class whose `@action` methods are orchestration recipes: prose instructions and a suggested tool sequence that an agent reads and follows, never Python that executes.

Scaffold from `formats/{format}/agent-with-actions-template.py`. Match `actions/examples/car.py` as the canonical shape.

---
# Concepts

## Actions are prose recipes, not code

- **`actions-are-recipes`** — `@action` methods are never executed. The body is a sequence of `self.<tool>()` calls interleaved with literal string `"""..."""` expressions. The framework reads AST — every `self.X()` in the body must reference a `@tool`, another `@action`, or a cross-instance call. No conditionals, no loops, no assignments.

## Tools do the real work

- **`tools-do-work`** — Real computation, file I/O, and external calls all go in `@tool` methods. Actions orchestrate; tools execute. An `@action` body that contains logic instead of tool calls is a violation.

## Docstrings are agent instructions

- **`docstrings-as-instructions`** — The method docstring and additional `"""..."""` expressions within an action body become the agent-visible instructions. Write them as commands: "Start the engine, then decide what to do according to personality." Not code comments. Multiple prose expressions within one action are all included.
- **`describe-what-things-do`** — Instructions state what a thing **does**, never what it does **not** do. "Log the result to `output.txt`." Not "Do not log to stdout." Negations describe absence; the agent needs presence. If a boundary matters, phrase it as the positive action that enforces it ("Write only to `output.txt`.") rather than as a prohibition.

## Keep actions thin

- **`keep-actions-thin`** — An action lists the tools the agent should consider, in suggested order. The `return` statement is a plain human-readable task statement; use `{parameter}` substitution for injected values. One action per high-level orchestration goal.

## Resources describe observable state

- **`resources-describe-state`** — Expose observable state as `@property @resource`. The agent reads `resources` from each tool response to track progress. Keep resources factual: current value, not desired outcome.

---
# Generate

1. Read § Concepts above and `actions/examples/car.py` — the canonical shape for a toolset with actions.
2. Scaffold from `formats/{format}/agent-with-actions-template.py`.
3. Fill every `{Placeholder}` — class name, constructor params, tools, action(s), return statement.
4. Place the generated file inside the appropriate domain folder with a matching manifest header on line 1.
5. Run **validate**.
