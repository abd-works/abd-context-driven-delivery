# Experiments — fewer CLI handoffs and fewer agentic tool operations

**Session:** optimize-running-context-tools-and-actions-through-the-cli-with-fewer-handoffs-and-fewer-agentic-tool-operations-16  
**Options catalog:** [options.md](options.md)  
**Corpus:** `sandbox/courier/courier.md` (unstructured text only; generated `.context` is produced by each run)

---

## What an experiment is

An **experiment** is a named collection of options from `options.md`, applied on its own git sub-branch, then measured by regenerating courier from the unstructured page.

It is not an options evaluation. Options stay in `options.md`. This sheet is only protocol + timings.

---

## Protocol

1. Name the experiment and list its option ids (for example `1e+5a+4c`). Baseline lists **none**.
2. Create a sub-branch from the session branch: `experiment/<name>`.
3. Apply only those option changes on that branch.
4. Kick the run with `/sub-agent` (`sub_agent.sub_agent:SubAgent`). The parent does **not** inline generate work and does **not** wait.
5. Inside the sub-agent, against `sandbox/courier` (source = `courier.md`):
   - Pair A: `/stories.story_map` then `/generate` — time **prompt → final story-map artifact**.
   - Pair B: `/clean_engineering.model` then `/generate` — time **prompt → final clean-engineering model artifact**.
6. When the sub-agent finishes, the parent adds one results row here.

**Clock:** wall time from the first tools CLI invoke of that pair to the moment the generated artifact is written and the pair’s generate turn is done. Record start/end ISO-8601 and elapsed minutes:seconds.

**Do not** AskQuestion for tool or fidelity — both pairs are already specified. **Do not** open a work session in the sub-agent (the listed action / context tool does that if needed).

---

## How to kick a run

Parent writes `_req.yaml` and runs:

```
python -m tools manifest sub_agent.sub_agent:SubAgent
python -m tools run _req.yaml
```

Request shape:

```yaml
toolset: sub_agent.sub_agent:SubAgent
action: run
context:
  workspace: c:\dev\abd-context-driven-delivery
  path: sandbox/courier
  session: optimize-running-context-tools-and-actions-through-the-cli-with-fewer-handoffs-and-fewer-agentic-tool-operations-16
arguments:
  tools:
    - context_tools.stories.stories:Stories
    - context_tools.clean_engineering.clean_engineering:CleanEngineering
  actions:
    - generate.generate:Generate
```

The parent then launches one non-blocking sub-agent (`kind: sub_agent` / `launch: non_blocking`) whose prompt is: follow this protocol for the named experiment; run generate with Stories at `story_map`, then generate with Clean Engineering at `model`.

---

## Results

| Experiment | Branch | Options | Pair A story_map+generate | Pair B model+generate | Notes |
|---|---|---|---|---|---|
| baseline | `experiment/baseline` | *(none + expander lists tools)* | **01:15** | **00:51** | First generate listed tools; wrote from inlined guidance; no domain `action: guidance` hop. [Baseline walker scratch rerun](ca3e3516-64ad-40bf-a55c-556c66c6514b) |
| single-command | `experiment/single-command` | **1b + 1c + 4c + 5a** + expander lists tools | **00:51** | **00:37** | One stdin `run -` per pair; tools listed; no invented `action: guidance`. [Single-command walker scratch](c5f1607b-3559-4784-b6aa-226cd6f15fa2) |
| thin-fidelity-format | `experiment/thin-fidelity-format` | smarter load: contexts by fidelity, examples by format; **no file split** | **00:44** | **00:35** | Expand **48,798** (from 74,019). No remanifest / invented `action: guidance`. [thin-fidelity-format](e442d1d8-55ec-4596-b204-84a0fc64db55) |
| thin-fidelity-format run 2 | same branch | + examples filename-match (`story_map` → story-map + thin-slice) | *(parent-inline)* | *(parent-inline)* | Expand **38,908**. Contexts already fidelity-sliced. Leftover fat is unfiltered **templates**. |
| thin-first-expand combined | `experiment/thin-fidelity-format` | all filters on **one** branch: contexts + examples + templates | **01:05** | **01:06** | Expand **17,767**. Fair first-time; hops 1; no remanifest / invented `action: guidance`. Did **not** beat single-command **00:51 / 00:37**. [thin-first-expand](4760f48e-5536-46ac-9f07-de5eef0247c8) |
| thin-first-expand + CE | same branch | same Stories filters + CE/DDD/UX/BDD contexts by H2; CE examples by suffix + drop `evals/` | **00:41** | **00:55** | Stories **17,767** / CE **45,100**. Pair A beat single-command **00:51**; Pair B missed **00:37** (beat prior **01:06**). Hops 1; no invented `action: guidance`. [thin-ce](01781ce8-dad9-49e7-9085-6857e1399b3e) |
| thin-templates | `experiment/thin-templates` | smarter load: templates by format + fidelity filename; **no file split** | **00:33** | **00:31** | Expand **52,878** (from 74,019). No remanifest / invented `action: guidance`. [thin-templates](9ede319c-0d8d-4ea6-9435-ef6293c99867) |
| channel-write | `experiment/channel-write` | one formatter `@agent_tool` writes the file (6c + 3a) | **01:15** | **00:11*** | Channel wrote both files. Stories emit too thin (lost actors / thin-slice). Pair B clock not fair (body staged before `run -`). **Not a keep.** [channel-write](experiment-channel-write-results.md) |

---

## Experiment notes

### baseline

Current harness and skills: write `_req.yaml`, `manifest`, then `run _req.yaml`. No option bundle applied. Expander lists tools on the first generate.

**Pair A 01:15** (14:03:09–14:04:24) — `sandbox/courier/.context/story-map.md`. Tools: `read_cdr_format`, `list_cdrs`, `write_cdr`, `guidance`, `finish_turn`. Wrote from inlined guidance.  
**Pair B 00:51** (14:04:31–14:05:22) — `sandbox/courier/.context/clean-engineering-model.md`. Tools: CDR + Drawio `create_diagram`/`scan`/`repair` + `finish_turn`. Drawio skipped (format is markdown).

### single-command (1b + 1c + 4c + 5a)

The first option bundle. **Single command** means each slash is one process: pipe a YAML fence to `python -m tools run -`.

| Option | What we apply |
|---|---|
| **1b** | `run` prints a slim `[run] invoking …` line. Skills drop the separate `manifest` step. |
| **1c** | Stdin only. No `_req.yaml` on disk. |
| **4c** | The skill/command already names the toolset and invoke. Do not remanifest. |
| **5a** | Harness `resolve_text` emits the filled YAML fence plus `python -m tools run -`. |

Not in this bundle: 1a (flags-only), 1d (new `invoke` subcommand), 1e (keep two commands). Pair A and pair B stay two slashes each; only the per-slash recipe changes.

Worktree: `C:\dev\abd-cdd-experiment-single-command` so this run does not share `sandbox/courier` with baseline. Thin-slice lives inside `story-map.md`.

**Pair A 00:51** (14:03:32–14:04:23) — one stdin `run -`; tools `read_cdr_format`, `list_cdrs`, `write_cdr`, `guidance`, `finish_turn`; wrote from inlined Stories guidance.  
**Pair B 00:37** (14:04:40–14:05:17) — one stdin `run -`; CDR + Drawio tools listed; Drawio skipped (markdown).  

Zero `_req.yaml`. No remanifest. No invented `action: guidance`. PYTHONPATH was the worktree.

### flatten (2a + 2b + 2c; 3 deferred)

Same instinct as section 3 (fewer hops by combining work). 3 stays deferred.

**3 research (done)** — [research-3-agent-instructions.md](research-3-agent-instructions.md). Nested `@agent_instructions` already merge in the first `action:` expand (`_ActionExpander`). 3C is already implemented. 3A would add hops. Real leftover hops are `@agent_tool` steps after expand (section 2) plus a first-expand author gap: `generate.py` writes `tool.guidance` without `()`.

**2 research (done)** — [research-2-flatten.md](research-2-flatten.md). Ignore 2d. Count only `tool:` / `action:` hops after the first expand.

Proposed apply (method names). No courier row until we pick:

| Id | Name | Swallows |
|---|---|---|
| 2B | lifecycle runner prelude/postlude | `begin`, `end`, `SessionLog.append`, `Turn.finish_turn` when session known |
| 2B | `/document` prelude | `Ddd.apply_document_workspace_default` |
| 2B | session-open prelude | `RecordDecisions.read_cdr_format` once (`write_cdr` stays agent-timed) |
| 2A | `Partition.partition_corpus_run` | `index`, `segment`, `verify_segment_completeness` |
| 2A | `Validate.run_validate_scan` | unlisted `tool.scanner.scan` |
| 2A | `Document.run_document_scan` | scan + Ddd workspace default |
| 2A | `Drawio.drawio_render_pipeline` | `create_diagram`, `scan`, `repair` launch |
| 2A | `Workflow.backlog_capture` | `compact_handoff`, `capture_backlog` |
| 2A | `Harness.deploy_generate` | `suggested_deploy_path`, `write_deploy` |
| 2C | `GrillContext.read_context_files` | repeated `read_context_file` |

Optional / lower: `satisfy_validate_and_fix`, `generate_via_bdd`, `capture_documents_pipeline`, `sketch_persist_draft`, `iterate_tick`, `echo_session_fenced`.

**leave:** grill AskQuestion + `write_grill_answer`; CE/Cdd companion `guidance`; diagnose; repair invent/map; session open when slug unknown.

Already flat: `Render.render`.
