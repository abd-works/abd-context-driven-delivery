# thin-templates results

- branch: `experiment/thin-templates`
- worktree: `C:\dev\abd-cdd-experiment-thin-templates`
- options: smarter load — templates by format alias + fidelity filename; **no file split**
- clock: first successful `python -m tools run -` of that pair → artifact written (ISO-8601 local)
- compare_to: single-command Pair A **00:51** / Pair B **00:37**

## In-process first expand

`Generate` + `Stories(fidelity="story_map", format="markdown", session=None)`

| | chars |
|---|---|
| today (unfiltered templates pack) | **74019** |
| thin-templates | **52878** |
| expected (options.md) | ~**52k** (drop ~22k) |
| delta | **−21141** |

Blob checks:

- Has `templates/md/story-map` body (`Story Map` / `Product / Feature Name`) and `thin-slice.md` (`Thin slicing`).
- Does **not** contain `stories-sketch` body (`Stories sketch — match active fidelity`).
- Does **not** contain java / ts / js / py story class templates (`StoryVerbNoun`, `_story.ts`, `_story.js`, `_story.py`).
- Does **not** inline `templates/md/scenario-outline.md` (no `## scenario-outline.md`). Remaining `scenario-outline` substrings are `examples.md` index + `examples/**/md/scenario-outline.md` — examples loading is the other experiment.
- Also kept `templates/md/story-context.md` because frontmatter `artifact: [story-map]`. Dropped `components/` (artifact `story-scenarios`) and `scenario-*.md`.

Listed tools on that expand: `read_cdr_format`, `list_cdrs`, `write_cdr`, `guidance`, `finish_turn` (walker). Not `[]`.

## Courier (this worktree only)

- pair_a_story_map_generate:
  - start: 2026-08-27T14:52:36
  - end: 2026-08-27T14:53:09
  - elapsed: **00:33**
  - hops: 1 (stdin YAML → `python -m tools run -` only)
  - first_generate_tools: [read_cdr_format, list_cdrs, write_cdr, guidance, finish_turn]
  - artifact: `C:\dev\abd-cdd-experiment-thin-templates\sandbox\courier\.context\story-map.md`
- pair_b_model_generate:
  - start: 2026-08-27T14:53:09
  - end: 2026-08-27T14:53:40
  - elapsed: **00:31**
  - hops: 1 (stdin YAML → `python -m tools run -` only)
  - first_generate_tools: [read_cdr_format, list_cdrs, write_cdr, create_diagram, scan, repair, finish_turn]
  - artifact: `C:\dev\abd-cdd-experiment-thin-templates\sandbox\courier\.context\clean-engineering-model.md`

vs single-command **00:51 / 00:37**: Pair A faster on the clock; Pair B similar. Blob shrink did not add hops.

## Notes

- Template files were **not** split or moved. `context_tools/stories/templates/` still has `md/`, `py/`, `ts/`, `js/`, `java/`, `stories-sketch.md`. No `templates/story_map/` pack. No `stories-templates.md`.
- `stories.md` section loading and `examples/` loading were **not** changed.
- Locator bug: `_locate_in_shared_templates` missed `stories-templates.md` and `locate()` only returned a file path, so the whole `templates/` folder was merged. Fix: when `format` is set, use `templates/{alias}/` (`markdown`→`md`, …) and keep fidelity filenames; when format is unset, merge the whole folder. Also return that folder from `locate()` instead of falling through to the meta dump.
- CE/BDD `{slug}-templates.{ext}` files still win when present (`clean_engineering-templates.py`).
- Zero `_req.yaml` on the worktree. Did not write `_req.yaml` on the session checkout. Never remanifested. Did **not** invent a domain `action: guidance` hop. Did not AskQuestion. Did not Generate on AgentBdd. `session=null`. PYTHONPATH was the worktree.
- `.\tools.ps1 run -` does **not** forward stdin (PowerShell function call). Pair CLI used worktree `.venv\Scripts\python.exe -m tools run -` with tools.ps1 PYTHONPATH + `$env:PYTHONIOENCODING=utf-8`.
- Thin-slice lives inside `story-map.md`. Pair B skipped Drawio (`format: markdown`).
- Specs: `asset_spec.py` (stories format folder vs whole pack) + `stories_spec.py` (story_map markdown templates slot). `mamba` 67/67 on those files + `markdown_extractor_spec.py`.
