# thin-fidelity-format results

- branch: `experiment/thin-fidelity-format`
- worktree: `C:\dev\abd-cdd-experiment-thin-fidelity-format`
- options: smarter load only — `contexts` by host fidelity (preamble + `## Shared rules` + `## {fidelity}`); `examples` by format alias (`markdown`→`md`, …). No file split. `templates/` unchanged.
- clock: first successful `python -m tools run -` of the pair → artifact written (ISO-8601 local). `session: null`. No remanifest. No invented domain `action: guidance`.
- compare: single-command walker Pair A **00:51** / Pair B **00:37**

## Expand (in-process)

`Generate.generate` + `Stories(fidelity="story_map", format="markdown", session=None)`

- instructions chars: **48798** (today **74019**)
- `## story_map`: present
- `## Shared rules`: present
- `## scenarios`: absent
- `## acceptance_tests`: absent
- `examples/**/py/**` (`/py/`): absent
- tools listed: `read_cdr_format`, `list_cdrs`, `write_cdr`, `guidance`, `finish_turn`

## Courier

Corpus: worktree `sandbox/courier` (source `courier.md` only). PYTHONPATH = this worktree.

### pair_a_story_map_generate

- start: 2026-08-27T14:50:51
- end: 2026-08-27T14:51:35
- elapsed: **00:44** (vs single-command **00:51**)
- hops: 1 (stdin YAML → `python -m tools run -` only)
- first_generate_tools: `read_cdr_format`, `list_cdrs`, `write_cdr`, `guidance`, `finish_turn`
- artifact: `C:\dev\abd-cdd-experiment-thin-fidelity-format\sandbox\courier\.context\story-map.md`

### pair_b_model_generate

- start: 2026-08-27T14:51:35
- end: 2026-08-27T14:52:10
- elapsed: **00:35** (vs single-command **00:37**)
- hops: 1 (stdin YAML → `python -m tools run -` only)
- first_generate_tools: `read_cdr_format`, `list_cdrs`, `write_cdr`, `create_diagram`, `scan`, `repair`, `finish_turn`
- artifact: `C:\dev\abd-cdd-experiment-thin-fidelity-format\sandbox\courier\.context\clean-engineering-model.md`

## Notes

- Kept one `context_tools/stories/stories.md` and the existing `examples/` tree. Filtering is expand-time only (`Instruction._expand_ref` + `thin_contexts_for_fidelity` / `thin_examples_by_format`). Kits without `## Shared rules` (Clean Engineering) keep full `# Contexts`. Example trees without `/{alias}/` (CE) stay unfiltered.
- Pair A: expander listed tools (not `[]`). Stories guidance inlined in the first generate payload. Did **not** invent a Stories `action: guidance` hop. Wrote `story-map.md` from those instructions. Listed CDR / `guidance` / `finish_turn` were not extra CLI hops. Thin-slice lives inside `story-map.md`.
- Pair B: expander listed tools (not `[]`). Drawio `create_diagram` / `scan` / `repair` listed with `format: markdown`; skipped those. Did **not** invent a CE `action: guidance` hop.
- Zero `_req.yaml`. Did not AskQuestion. Did not open a work session / `finish_turn`. Did not Generate on AgentBdd. Did not write under the session checkout except this results file.
- PowerShell does not forward stdin into `.\tools.ps1`; first successful invoke used worktree `.venv\Scripts\python.exe -m tools run -` with the same PYTHONPATH as `tools.ps1`. Two earlier stdin attempts (`tools.ps1` empty stdin; Generate `workspace=` kwarg) failed before the clocked Pair A invoke.
- Specs: `mamba` `markdown_extractor_spec.py` + `instruction_spec.py` + `stories_spec.py` — 85 examples, 0 failures.

## Run 2 — examples filename-match (same branch, no new agent)

Added `thin_examples_by_fidelity` after the format filter. `story_map` keeps `story-map.md` + `thin-slice.md` only. `scenarios` keeps `scenario-*`. No match (CE / acceptance_tests code trees) leaves the format-filtered set. Contexts stay fidelity-sliced (run 1). Templates still unfiltered. Files not split. Session checkout not used for the code change.

Worktree specs: `markdown_extractor_spec.py` + `stories_spec.py` — 61 examples, 0 failures.

### Expand (in-process)

`Generate.generate` + `Stories(fidelity="story_map", format="markdown", session=None)`

- instructions chars: **38908** (run 1 **48798**, unfiltered **74019**)
- `## story_map` / `## Shared rules`: present
- `## scenarios` / `## acceptance_tests`: absent
- `examples/**/py/**`: absent
- `examples/**/md/scenario-*.md`: absent (filename match)
- Remaining `scenario-main-flow` / `scenario-outline` strings are **unfiltered templates**, not examples
- tools listed: `read_cdr_format`, `list_cdrs`, `write_cdr`, `guidance`, `finish_turn`

### Courier (parent-inline on this worktree)

Not a sub-agent. Stdin `run -` then write. Same corpus. Compare **expand chars** to run 1; these clocks are this session rewriting a known map, not a blind first read of a 74k blob.

- pair_a: 2026-08-27T15:49:01–15:49:35 **00:34** — artifact `sandbox/courier/.context/story-map.md`
- pair_b: 2026-08-27T15:49:35–15:49:47 **00:12** — CE still unfiltered; existing model confirmed. Do not treat as a beat of run 1 **00:35**.
