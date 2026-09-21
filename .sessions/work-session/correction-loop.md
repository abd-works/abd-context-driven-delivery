# Correction loop

Each session is a folder. Each run is a file in that folder.

```
.context/correction-sessions/
  correction-loop.md
  CORRECTIONS-CLI.md
  corrections-cli.mjs
  _current
  {session-name}/
    _correction-approach.md
    corrections-{datetime}.md
```

`_correction-approach.md` is the procedure: which context tools, in what order, and after which steps the working set is injected. Each `corrections-{datetime}.md` is one run — ranked rules with ★ and Bad/Good — not the prompt.

```sh
node .context/correction-sessions/corrections-cli.mjs list
node .context/correction-sessions/corrections-cli.mjs start-session <name> [--from <name>]
node .context/correction-sessions/corrections-cli.mjs next-run
node .context/correction-sessions/corrections-cli.mjs list-rules <tool> [fidelity]
node .context/correction-sessions/corrections-cli.mjs add-correction <rule-slug>
```

---

## Counts

`★` is the **session** total for that slug. It is shared across every run in the folder. It never resets when you open a new run.

Walk run files **newest → oldest**. The first heading you find for a slug is the session `★`. Do not add the last run’s `★` to the run before it.

Older run files still matter: they hold totals and Bad/Good for slugs the newest file does not mention.

A heading is `## \`slug\` ★N`. Ignore leftover `(session: …)` / `(run: …)` suffixes when reading; do not write them on new headings.

`list` builds that merged index. `add-correction` looks up the session `★` the same way, writes the bump onto **this** run’s file, and leaves older files as they were.

---

## 1. Start a session

Create `.context/correction-sessions/{session-name}/` and write `_correction-approach.md`. Name the context tools and fidelities in play (for example `stories` `scenarios`, `clean_engineering` `model`).

**Get at a context tool.** Source of truth is `c:\dev\abd-context-driven-delivery\context_tools\{tool}\{tool}.md`. In the agent, call `{tool}_guidance` (`stories_guidance`, `clean_engineering_guidance`, `ddd_guidance`, …). Shared rules sit under `## Shared rules`. Fidelity rules sit under `## {fidelity}` → `### Rules`. Each rule is a backtick slug (`verb-noun-format`, `translate-invoke-transform`).

**Blank session.** No prior run file. Pool those `### Rules` (and Shared rules) for the tools in the approach, plus any seeds we pick. No recency, no ★. There is no CLI command that lists every tool’s rules; read those sections or call guidance. `add-correction` can already pull a *known* slug from another tool’s `{tool}.md`.

**Session based on a previous session.** Copy or edit the approach. Pool the same context-tool Rules plus `list --from-session {that-name}` — the merged index of that folder, newest → oldest. Do not copy a run file wholesale. Keep rules that match this session’s outcome. Recency and ★ only sort that already-matched set. A slug that carries over starts this session at the inherited `★`.

---

## 2. Start a run

Create `corrections-{datetime}.md` in the session folder. That file is this run. A blank first run is expected.

Build a working set of about 5–8 short rule bodies from:

- `list` (merged session index, ranked by ★) — matching slugs for this generate.
- Context-tool Rules for this generate — `{tool}_guidance` / `{tool}.md` `### Rules` (fills the set when the index has no hits yet).
- The rule just logged, even at ★1.

Do not treat the new empty run file as the whole ledger. Inject the merged set into generate and into the check after. Skill guidance, template, and examples stay (how to produce). Skill Rules are the catalog the selector reads, not a second checklist. The worker holds to the injected set only. A ledger slug in the set overrides the same slug in the skill.

**During the run — do this without being asked.** Write the artifact against the working set. Check the same set on the way out (tail-check). Do not wait for “please validate.” Tests, and later scan/validate, catch the rest.

**When a miss is spotted** (tail-check or the user): fix the artifact first, then `node .context/correction-sessions/corrections-cli.mjs add-correction <rule-slug>`. That looks up the session `★` across prior runs, writes the rule onto **this** run at `★ + 1`, and scaffolds from any `{tool}.md` when the session has no slug yet. Add a Bad/Good pair only when existing examples would have missed this shape. No matching rule in the session or in any `{tool}.md` → create one at ★1 with a `concept:` tag. A small miss still logs; ★ is how severe/frequent it has been, not a gate on whether to update.

This run file lists slugs that fired **this** generate. That is the log of the pass, not the lookup rule.

---

## 3. Start the next run

Create a new `corrections-{datetime}.md`. Repeat step 2. `list` walks every run in the folder, newest first. The just-logged rule from the last complaint is in the set.

Context-tool Rules carry the working set until this session’s run files have hits.
