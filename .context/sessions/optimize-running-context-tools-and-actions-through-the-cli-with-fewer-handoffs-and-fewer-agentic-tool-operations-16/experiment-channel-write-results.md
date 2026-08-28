# channel-write results

- branch: `experiment/channel-write` (`ff6eb1f` from session `11527eb`)
- worktree: `C:\dev\abd-cdd-experiment-channel-write`
- options: one `@agent_tool` `generate_output` that parse/renders via the existing Stories/CE formatter and writes `.context/` (old 6c). Header + `SessionLog.append` run inside that tool (old 3a). `Generate.add_generate_header_to_generated` is also `@agent_tool` so expand lists it. CE markdown no longer walks `drawio.render` on generate expand.
- clock: first successful `python -m tools run -` of the pair → artifact written (ISO-8601 local). `session: null`. No remanifest. No invented domain `action: guidance`.
- compare: thin-ce **00:41 / 00:55**; single-command **00:51 / 00:37**. Isolated thin-templates **00:33 / 00:31** are not the bar.

## What changed

- `Stories.generate_output(content="")` `@agent_tool` — channel parse/render, write `sandbox/courier/.context/story-map.md`, prepend header, log.
- `CleanEngineering.generate_output(content="")` `@agent_tool` — same for markdown/json/code; `drawio.render` only when `format` is drawio.
- `generate.generate_header_block` + `add_generate_header_to_generated` as `@agent_tool`.

## Courier

Corpus: worktree `sandbox/courier` (source `courier.md` only). PYTHONPATH = this worktree. Did not Read leftover `story-map.md` / `thin-slice.md` / `clean-engineering-model.md` before overwrite. Channel **did** write both artifacts (not Cursor Write).

### pair_a_story_map_generate

- start: 2026-08-27T19:27:32
- end: 2026-08-27T19:28:47
- elapsed: **01:15** (vs thin-ce **00:41**; vs single-command **00:51**)
- hops: 2 stdin `run -` (Generate expand, then Stories `tool: generate_output`). No remanifest.
- first_generate_tools: `read_cdr_format`, `list_cdrs`, `write_cdr`, `guidance`, `generate_output`, `add_generate_header_to_generated`, `finish_turn`
- artifact: `C:\dev\abd-cdd-experiment-channel-write\sandbox\courier\.context\story-map.md`
- channel wrote the file: **yes** (CLI `result` path). Model did not Write.
- quality: **too thin**. Outline `(E)/(S) Actor -->` collapsed to `#` / `##` / `-` with **no actors**. No thin-slice, no Sources. Python docstring header on markdown.

### pair_b_model_generate

- start: 2026-08-27T19:29:25
- end: 2026-08-27T19:29:36
- elapsed: **00:11** (vs thin-ce **00:55**; vs single-command **00:37**)
- hops: 2 stdin `run -` (Generate expand, then CE `tool: generate_output`). No remanifest.
- first_generate_tools: `read_cdr_format`, `list_cdrs`, `write_cdr`, `generate_output`, `add_generate_header_to_generated`, `finish_turn` — Drawio `create_diagram` / `scan` / `repair` **not** listed (markdown path).
- artifact: `C:\dev\abd-cdd-experiment-channel-write\sandbox\courier\.context\clean-engineering-model.md`
- channel wrote the file: **yes**. Model did not Write.
- quality: usable class blocks, but thinner than a full agent write (no language companion, module meta flattened). Clock is optimistic: CE body was staged before this pair’s first `run -`.

## Verdict

**Too thin / miss.** Channel write owns the file and drops Drawio from markdown generate, but Stories emit is the wrong shape versus agent Write. Pair A **01:15** missed thin-ce **00:41** and single-command **00:51**. Pair B **00:11** is not a fair beat of **00:37** / **00:55** (invent was off that pair’s clock). Inventing still needs the expand blob; empty `content` would be faster and emptier. Not a keep.
