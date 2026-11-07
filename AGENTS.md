# ABD Context Driven Delivery

Agentic tools that bring agile product, delivery, and engineering practices to AI work. Practices are lenses on the work; actions are what you do with a lens; fidelities are how deep you go.

## Layout

- `cdd_guidance/practices/` — Stories, DDD, UX, Clean Engineering, BDD. Each practice is one `{practice}.md` (Overview, shared rules, a section per fidelity with its Rules) plus a thin `{practice}.py`, templates, `_examples/`, a `graph_practice.py` that registers what the knowledge graph reads from it, and `rules/rule_examples.py`, the spec support that checks a failing and a repaired example against one rule.
- `cdd_guidance/actions/` — the shared verbs: partition, document, sketch, grill, generate, validate, satisfy, render, iterate, repair.
- `cdd_guidance/patterns/`, `cdd_guidance/builders/` — stack patterns (LERN, MERN) and builders for new toolsets and practices.
- `cdd_guidance/rules/` — always-on rules, installed into every IDE. `cdd_guidance/references/` — reference docs installed to `<ide>/references/`.
- `cdd_guidance/agents/` — Discoverer, Specification, Implementation, Context agents.
- `harness/` — the framework. From the bottom up: `name` and `annotations` (the decorator annotations), `agent_tools` (toolsets and the per-call `ToolCall`), `markdown`, `guidance` (practice and action catalogues, and the stages in `stages.py`), `guidance_actions`, `installation`, `process`, `hooks`, `mcp`, `graph`; then `installer`, `diagnostics` (server health and the install probes), `chat` (reaching a live Claude Code chat), `catalog_generator`, `design_canvas`, and the `chat-ui` plugin.
- `harness/` imports nothing from `space/`, `tools/`, or `cdd_guidance/`. They register with the framework instead: `space/session` with `ToolCall.open_sessions_with`, the prompt notifier with `HookServer.show_toasts_with`, and each practice through its `GraphPractice`. Keep it that way, so the framework can change and be tested without the code built on it.
- `space/` — the work: `session` (sessions, their log, files, handoffs, and decision records), `repo` (branches, commits, worktrees), and the Session Board (`space/kanban`). `tools/` — one module of independent toolsets, one package each (sub-agent hand-off, echo, Granola, prompt log, prompt notify), sharing the card `tools/.context/module-context.md`; the file manager keeps its own card until it moves into `space/session`.

| Practice | Discovery | Specification | Implementation |
|---|---|---|---|
| Stories | story_map | scenarios | acceptance_tests |
| DDD | bounded_context | model | tactics |
| UX | ia | mockup | front_end_code |
| Clean Engineering | modules | model | code |
| BDD | behavior | realization | development |

## Where context lives

- Root `.context/` — `cdd-approach.md` (stages and practices), `module-context.md` (every module's purpose, seams, constraints), `principles/`.
- Every module folder has its own `.context/` (`module-context.md`, `domain-context.md`, `cdr/` decisions) and some have an `AGENTS.md`. Read them before changing that module.
- `catalog/workflow.md` — how practices, actions, and fidelities compose.

## Generated, never edited

`.claude/`, `.cursor/`, `.github/` installs, `.mcp.json`, and the `cdd` entry in `~/.claude.json` are written by the installer from annotated operations (`@agent_toolset`, `@agent_tool`, `@agent_instructions`, `@skill`, `@command`, `@rules`, `@mcp`, `@hook`, `@noDeploy`). Change the source in `cdd_guidance/` or `harness/`, then reinstall:

```
python scripts/install.py --ide Claude     # or Cursor, "VS Code", Kilo
```

## Setup and tests

```
python -m venv .venv && .venv/bin/pip install -e .     # Windows: .venv\Scripts\pip
.venv/bin/mamba --format documentation path/to/thing_spec.py
```

`scripts/test.ps1` runs the suite (`-Suite heavy` for `*_heavy_spec.py`, which start servers or browsers). Cloud sessions run `scripts/cloud-setup.sh`.

Specs are Mamba: `describe` a domain subject, nest `with` / `that` states (never `when`), one outcome per `it`, ordered as a usage story. Practice rules under `.claude/rules/` apply by path.
