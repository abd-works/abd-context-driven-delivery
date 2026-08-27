# Options — fewer CLI handoffs and fewer agentic tool operations

**Session:** optimize-running-context-tools-and-actions-through-the-cli-with-fewer-handoffs-and-fewer-agentic-tool-operations-16  
**Issues:** [#16](https://github.com/abd-works/abd-context-driven-delivery/issues/16), [#8](https://github.com/abd-works/abd-context-driven-delivery/issues/8), [#17](https://github.com/abd-works/abd-context-driven-delivery/issues/17)  
**Timings:** [experiments.md](experiments.md)  
**Parked ids:** [backlog.md](backlog.md) deferred

Evaluate only here. Old 1a–7h labels live in the backlog so this page can stay experiment-shaped.

---

## Settled (do not re-open)

| What we tried | Result |
|---|---|
| **Walker** — listed recipe steps on the first generate (`tools:` not `[]`); host guidance inlined | Agent stopped inventing a domain `action: guidance` hop |
| **Single-command** — `run` slim header + stdin `run -` + skill is the catalog + harness emit (old 1b, 1c, 4c, 5a) | Pair A **01:15 → 00:51**, Pair B **00:51 → 00:37**. One process per pair. |

**Locked seam:** `@agent_instructions` are parsed, not executed. `@agent_tool` bodies run. Do not author from the `.py` (old 6a stays rejected).

Nested expand (old 3c / 7f) is already how Generate works. The leftover is the **size** of that first payload, not a missing second CLI.

---

## What is still expensive

After single-command + walker, Pair A is **one** `run -` (~0.1s expand) then **~51s** of the model reading ~74k characters of inlined guidance and writing the story map.

Listing unused tools (`finish_turn`, CDR, Drawio) did **not** move that clock. Remanifest, `_req.yaml`, and a second guidance action are gone.

Issue 17 as “cache so hop 2 can skip remanifest” does not apply: there is no hop 2 on this pair.

---

## Viable next experiments

Each row is one courier-measurable bundle (same protocol as [experiments.md](experiments.md)). Do not split these back into 1a/4b-style micro-ids unless a bundle itself needs a fork.

### Thin first expand (smarter load — do not split files)

**Constraint:** keep `stories.md`, `examples/`, and `templates/` as they are. No `fidelities/story_map.md`, no per-fidelity copies, no `@focus` layout that requires `{group}/{value}.md`. Filter at expand time.

Current first generate is **74,019** chars. Almost all of it is unfiltered `examples/` + `templates/` + the whole `# Contexts` section.

| Experiment | Load rule | Do not touch | Expected blob (story_map + markdown) |
|---|---|---|---|
| **thin-fidelity-format** | `contexts`: preamble + Shared rules + `## {fidelity}` only (whole `# Contexts` if fidelity is unset). `examples`: only files under the active format alias (`markdown`→`md`, `python`→`py`, …), using default format when the caller omitted one. | `templates/` | ~74k → ~**40k** (contexts −6k, examples drop `py/` −16k; leftover is all `md/` examples including scenarios) |
| **thin-templates** | `templates`: only `templates/{format-alias}/`, then filenames for this fidelity (`story_map` → `story-map.md` + `thin-slice.md`). Drop `stories-sketch.md` from generate. | `stories.md`, `examples/` | ~74k → ~**52k** (drop ~22k of wrong-format / sketch / scenario templates) |
| **thin-examples-pick** | *Analysis only — do not implement yet.* See below. | — | — |

Do **not** combine the first two on one branch. Templates live in a different locator path; experiment 1 will not fix them. Clock vs single-command Pair A **00:51**. Hop back to remanifest / invented `action: guidance` = miss.

#### Do not load every example (analysis, not a courier row yet)

After **thin-fidelity-format**, markdown `story_map` still inlines **every** `examples/**/md/*` file (~16k), including `scenario-main-flow.md` (largest single file in the blob). Format ≠ fidelity.

| Approach | Verdict |
|---|---|
| **“AI, look in `examples/` and pick the relevant ones”** | Weak first bet. `examples.md` already tags path → purpose, but `read-all-source-context-in-full` will make the model Read the lot anyway. Pointer + hop also fails the clock rule. |
| **Most recent 5 / 10** | Do not. One corpus today (`manage-customer-orders`). Recency is git mtime, not quality; the canonical tree would lose to a newer junk example. |
| **Same smarter load, filename match** | Do this when we touch examples again: `story_map`+`md` → `story-map.md` + `thin-slice.md` only. Still one folder, no split. That is the fidelity cascade on examples — fold into a later **thin-fidelity-format** follow-up, not a recency experiment. |
| **Canonical / tagged pick when n>3** | Only after several same-fidelity same-format examples exist. `examples.md` is already the tag index. |

Do not implement **thin-examples-pick** until **thin-fidelity-format** has a courier row.

### Channel write

**Question:** when a formatter already exists, does one `@agent_tool` that calls the channel (old 6c, plus deterministic header/log as tools — old 3a) beat “read 74k and Write the file”?

Stories markdown / CE markdown already have emitters. Agent still chooses when there is no channel (grill, invent/map).

**Risk:** empty or wrong artifact if the channel is thinner than the agent write. Keep grill interview agentic.

### Same-kit tool list

**Question:** leave the fine `@agent_tool`s; one YAML (or one shell) runs `tool: a` then `tool: b` on the **same** toolset with **no** remanifest (old 2d).

Does **not** shrink the first generate blob. Measures grill / validate / CDR sequences, or a generate that actually *uses* listed tools. Wrong bundle for “make story-map generate faster” unless that pair starts calling `finish_turn` / `write_cdr`.

**Risk:** still one model turn per tool if the runner requires “read resources before the next.”

### Lifecycle in-process

**Question:** `begin` / `end` / SessionLog / `finish_turn` run in the expand process (old 2b, 7g) so they are not listed and not a later slash.

Small effect on the 51s unless it also **drops CDR / turn prose** from the first payload (then it overlaps Thin first expand). Worth it as hygiene + fewer future hops, not as a courier-map speed bet on its own.

**Risk:** blurs “instructions are never executed” unless prelude is an explicit mark.

### Grill explore (separate corpus)

**Question:** batch reads or return paths and let Cursor Read (old 2a / 2c / 7e). Grill questions stay multi-turn.

**Do not** use the courier story-map clock. Different pair: grill against an existing `.context` tree.

---

## Out of scope for the next courier row

Workspace root, AskQuestion, `gh` Status names, multi-folder deploy, MCP, slim-manifest-for-its-own-sake, `tools serve`. Parked on the backlog. They are real taxes; they are not this 51s.

---

## Suggested order

1. **thin-fidelity-format** then **thin-templates** — separate branches / sub-agents; smarter load only.  
2. **Channel write** — if a formatter can own the file.  
3. **Same-kit tool list** — when the clock is “many `tool:` hops,” not “one fat generate.”  
4. **Lifecycle in-process** — if Thin first expand still leaves CDR/turn text, or `/finish-turn` comes back as a hop.  
5. **Grill explore** — own experiment, own corpus.
