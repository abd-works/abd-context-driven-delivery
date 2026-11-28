# Cog: theme 7, switching a practice off while work on it is under way

Build `9f3c29d38` (worktree nostalgic-mclaren-b1ae7c). I worked in the sandbox `C:\dev\_et\after-1-2-1\cog`: the `work/repo` folder holds the Bookshop story fixture plus UX and DDD files written while those practices were on. The cdd server ran on port 8961 with `CDD_HOME=cog/cdd_home`, and every call went over real MCP HTTP (`scripts/cdd.py`, with the `X-CDD-Project` header). Notes are in `C:\dev\_et\after-1-2-1\cog\notes.md`.

## Defects (6, one of them a question)

| File | Severity | In one line |
|---|---|---|
| cog-05-two-practice-toggles-at-once-lose-one | wrong result | Two toggles at once (UX off, DDD off) both answer OK, and one is undone. It happened in 4 of 4 runs. |
| cog-01-validate-two-practices-misses-ux-schema-error | wrong result | Validating `ux-ia ddd-bounded-context` together hides UX's checked conforms-to-schema error, so the board shows ux-ia as done. Both reports hold both practices' rules. |
| cog-04-render-ux-json-read-as-saved-graph | blocks work | A render of ux-ia from `ux/ux.json` to drawio or whiteboard fails with SavedGraphOutdated, because any `.json` source is read as a saved graph. |
| cog-02-toggle-unknown-name-answers-success-changes-nothing | misleading message | Toggling `astrology`, `UX`, `Specification` or `Markdown` answers OK, raises the version and commits to main, but changes nothing. |
| cog-03-question-every-practice-off-turns-every-practice-on | question | With no practice on, the selection and the generate command cover all five practices, including CE and BDD, with `format=python`. The board marks Discovery done. |
| cog-06-first-validate-writes-graph-into-project-context | cosmetic | The first validate leaves an untracked `.context/graph.json` in the project, and the ticket's file list shows it. |

## What held up

These behaviours matched the scenarios and the 2026-11-25 decision that switching a practice off changes only what the board and chat show:
- **Progress is kept.** The progress a fidelity had (done, violations, report) stays through off and back on, for UX, DDD and BDD.
- **Formats are kept.** The formats chosen for UX IA and the UX mockup stay through off and on, even when a format group is changed while UX is off.
- **Explicit actions still work.** Generate and validate named explicitly on a practice that is off still run and log, and the practice stays off.
- **The automatic check skips practices that are off.** `session.check_changed_artifact` checks only the fidelities of practices that are on. A file shared between two practices, such as a story spec used by BDD and Stories, is checked only for the practice that is on.
- **Files of a practice that is off are hidden, not lost.** They leave the linked listing (`is_listed` false) but stay in `ticket.root_files`.

## Confusing places

- **Two calls disagree on whether a file is listed.** While UX is off, `ticket.fidelity_files` for ux-ia says `is_listed: false` and `fidelity-progress.files` for the same fidelity says `true`. I did not report this.
- **Every toggle makes a git commit on main**, including toggles that change nothing (see cog-02).
- **UX IA declares a json output, but `generate format=json` is refused** with "ia does not write json". I noted this and did not report it, because the last round had already left data formats undecided.
- **The automatic check logs its validate line as `no-chat`**, even though the call carried a chat header.

## Not reached

- The Files app and the board in a browser. I tested only through their server calls; I did not open the pages or watch toggles redraw.
- `session.file` callouts filtered by a practice that is off.
- `graph_trees` for a practice that is off.
- Iterate, sketch and document on a practice that is off.
- Clean Engineering toggled off and on with code files.
- A toggle made while a long validate is still running.

## Where the risk still is

- **Two callers changing one session at once** (cog-05). The practice list is read outside the record's update and written back whole. Other read-then-write paths on session.json, such as format groups and stages, are probably exposed the same way; I tested only practices.
- **Actions that take several guidance in one call** (cog-01). Each practice's graph rules and hits should stay its own; what the board shows as done depends on it.
- **What "no practice selected" means** (cog-03). The rule "a filter with nothing selected filters nothing" makes sense for viewing files, but here it also drives the commands a chat runs.
