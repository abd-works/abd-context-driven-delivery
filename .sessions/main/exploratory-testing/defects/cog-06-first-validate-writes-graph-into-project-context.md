# cog-06 The session's first validate writes a graph.json into the project's own .context, which then shows among the ticket's files

**Title** - The first `validate.validate` in session checkout-flow wrote `work/repo/.context/graph.json` (untracked, 212 KB, practices stories, ddd and ux: the ones on then), beside the session's own `.sessions/checkout-flow/graph.json`.

**Charter** - theme 7. **Tester** - Cog.

**Story** - no scenario covers this. `harness/graph/graph.py` line 1428 promises: "A session's graph is written into the session's own folder (`.sessions/<session>/graph.json`), never the project's `.context`".

**Module and class** - where the validate's graph is built and saved: `harness/graph/graph_build.py` (a build "saves the graph it built in its folder's graph.json") reached from `cdd_guidance/actions/validate/validate.py` *Validate*. Not narrowed further.

**Severity** - cosmetic (a stray, untracked file in the person's project: `ticket.root_files` lists `.context/graph.json`, so the Files app shows it, and a person committing the whole worktree commits it). It also holds only the practices that were on at that moment, so a reader of it after a practice is switched on sees an old graph without it.

## Steps

Sandbox and server as in cog-01; `work/repo` clean after `git commit` of the Bookshop files.

1. `ticket.create {"title":"Checkout flow"}`
2. `generate.generate {"guidance":"ux-ia ddd-bounded-context session=.sessions/checkout-flow/session.json"}`
3. `validate.validate {"guidance":"ux-ia ddd-bounded-context session=.sessions/checkout-flow/session.json","paths":["ux/ux.json",".context/bounded-context-map.md"]}` (16:54:09 to 16:54:12 UTC)
4. `git status --short` and `ticket.root_files {"ticket":"checkout-flow"}`

## Expected

The graph saved only under `.sessions/checkout-flow/` (and the checked graphs under its `.context/checked-graphs/`); nothing new in the project's `.context`.

## Actual

`?? .context/graph.json`, modified 16:54:10 UTC, keys `version, overlays, practices` with practices `['stories', 'ddd', 'ux']`. `ticket.root_files` lists `.context/graph.json` with no fidelity. `.sessions/checkout-flow/graph.json` exists as well.

## Tier that should catch it

Heavy (a real validate in a session on a scratch repository, then a check that the project's `.context` holds no graph.json). `graph_json_spec.py` checks the folder save for a graph no session holds, not that a session's validate leaves the project alone.
