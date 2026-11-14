# ABD Context Driven Delivery

Agentic tools that bring agile product, delivery, and engineering practices to AI work. Practices are lenses on the work; actions are what you do with a lens; fidelities are how deep you go.

## Layout

- `cdd_guidance/practices/` — Stories, DDD, UX, Clean Engineering, BDD. Each practice is one `{practice}.md` (Overview, shared rules, a section per fidelity with its Rules) plus a thin `{practice}.py` (whose class names the practice's part in the knowledge graph, a *PracticeReading* kept in `model/graph_reading.py`), templates, `_examples/`, and `rules/rule_examples.py`, the spec support that checks a failing and a repaired example against one rule.
- `cdd_guidance/actions/` — the shared verbs: partition, document, sketch, grill, generate, validate, satisfy, render, iterate, repair.
- `cdd_guidance/patterns/`, `cdd_guidance/builders/` — stack patterns (LERN, MERN) and builders for new toolsets and practices.
- `cdd_guidance/rules/` — always-on rules, installed into every IDE. `cdd_guidance/references/` — reference docs installed to `<ide>/references/`.
- `cdd_guidance/agents/` — Discoverer, Specification, Implementation, Context agents.
- `harness/` — the framework. From the bottom up, as the imports run: `annotations` (the decorator annotations, and *Name*, the one case conversion every published name goes through), `markdown`, `agent_tools` (toolsets and the per-call `ToolCall`), `installation` (the Installer and what it publishes with; `mcp` and `hooks` register their installations with it), `process` (beside them, importing nothing), `hooks`, `mcp`, `guidance` (practice and action catalogues, and the stages in `stages.py`), `guidance_actions`, `graph`; then `diagnostics` (server health and the install probes), `chat` (reaching a live Claude Code chat), `catalog_generator`, `design_canvas`, and the `chat-ui` plugin.
- `harness/` imports nothing from `space/`, `tools/`, or `cdd_guidance/`. They register with the framework instead: `space/session` with `ToolCall.open_sessions_with`, the prompt notifier with `HookServer.show_toasts_with`, and the practices, actions, and patterns from their package `__init__.py` with `PracticeCatalogue.register`, `ActionCatalogue.register`, and `PatternOverlays.register`; a session makes the practices' instances once and gives its knowledge graph. Keep it that way, so the framework can change and be tested without the code built on it.
- `space/` — the work: `session` (sessions, their log, their files and the file manager that reads them, handoffs, and decision records), `repo` (branches, commits, worktrees), and the CDD Kanban (`space/kanban`). `tools/` — one module of independent toolsets, one package each (sub-agent hand-off, echo, Granola, prompt log, prompt notify), sharing the card `tools/.context/module-context.md`.

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

`scripts/test.ps1` runs one of three tiers. Cloud sessions run `scripts/cloud-setup.sh`.

| Tier | Files | What belongs there |
|---|---|---|
| `-Suite unit` (default) | `*_spec.py`, `*_story.test.py`, story tiers | Fast: an example runs in microseconds to milliseconds, so hundreds run in seconds. An example over `-ExampleBudgetMs` (100 ms) fails its file; the run lists each one. Use fakes (`MockGit`) and shared fixtures. |
| `-Suite heavy` | `*_heavy_spec.py` | Real resources: git, the cdd server, the hook daemon, the installer, worker graph builds, big loads. One file at a time. |
| `-Suite e2e` | `*_e2e_spec.py`, `*_agent_spec.py` | The beasts: a real browser through Playwright, and agentic BDD that drives a real agent. The only tier that may start an agent. |

The rule for which tier a test belongs in is BDD's `tier-by-speed` (`cdd_guidance/practices/bdd/bdd.md`, development).

Specs are Mamba: `describe` a domain subject, nest `with` / `that` states (never `when`), one outcome per `it`, ordered as a usage story. Practice rules under `.claude/rules/` apply by path.
