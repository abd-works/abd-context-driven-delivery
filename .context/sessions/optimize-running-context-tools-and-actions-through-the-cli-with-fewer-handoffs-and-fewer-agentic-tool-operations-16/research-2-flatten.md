# Research 2 — flatten (2A / 2B / 2C)

**Session:** optimize-running-context-tools-and-actions-through-the-cli-with-fewer-handoffs-and-fewer-agentic-tool-operations-16  
**Experiment:** `flatten` — count only hops where the agent must issue another `tool:` or `action:` CLI run **after** the first expand. Nested `@agent_instructions` inlined in the first payload are **not** hops (section 3). Grill `AskQuestion` stays agentic.

**Hop detection method:** `ActionExpander.parse_body` `tool_steps` on representative instances, plus manual trace of cross-toolset / `mode=tool` / for-loop gaps (expander does not walk `self.*` or cross-provider calls inside `for tool in …` bodies).

---

## context_tools/base/base_context_tool.py — `BaseContextTool`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `guidance` |
| `@agent_tool` | *(none on base)* |

**CLI / slash:** Domain skills (`/stories`, `/bdd`, …) expand `guidance` on the host tool; lifecycle kits call `tool.guidance` inline during `/generate`, `/validate`, etc.

**After first expand — separate hops:**
- None from base itself when reached via lifecycle expand (`tool.guidance` inlines because host `mode=action`).

**Already in-process / inlined:**
- `contexts`, `examples`, `templates`, `scaffold` — `@instruction` slots expanded into prose.
- `session_guidance` — `@instruction` delegate to `WorkSession`.
- `generate_output`, `generate_fixes_from_validate`, `render` — plain Python defaults (expander may ` _run_plain_call` during parent walk; no extra CLI hop).
- Fidelity shims `generate_{f}`, `validate_{f}`, `satisfy_{f}` — plain methods delegating to lifecycle actions.

### Target

**no flatten** — base has no extra agent hops beyond what callers defer via `mode=tool`.

---

## context_tools/cdd/cdd.py — `Cdd`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `guidance` |
| `@agent_tool` | *(none)* |

**CLI:** `/cdd` skill → `action: guidance` on `context_tools.cdd.cdd:Cdd`.

**After first expand — separate hops (expander `tool_steps` on `guidance`, fidelity=discovery):**
- `guidance` ×4 — one deferred hop per stage child (`Stories`, `Ddd`, `Ux`, `CleanEngineering`) because loop sets `context_tool.mode = "tool"` before `context_tool.guidance()`.

**Already in-process / inlined:**
- `super().guidance()` — parent `BaseContextTool.guidance` inlined.
- Lifecycle (`/generate`, …) — not on `Cdd` directly; orchestration prose only.

### Target

**leave** — agent must choose which stage child to run and remanifest each toolset (`Stories`, `Ddd`, `Ux`, `CleanEngineering`). Flattening would hide intentional cross-toolset boundaries.

---

## context_tools/stories/stories.py — `Stories`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `guidance` |
| `@agent_tool` | `transform`, `render` |

**CLI:** `/stories` → `guidance`; `/generate` + `tools: [Stories]` → lifecycle inlines `tool.guidance` + `tool.generate_output()`; `/render` → `Render.render` → `tool.render(format, content)`.

**After first expand — separate hops:**
- `guidance` on **CE companion** when `Stories.fidelity=acceptance_tests` (expander: `('guidance',)` — `self.ce().guidance()` with `ce.mode=tool`).
- `diagnostic().diagnose()` — prose instructs agent to call; `@sub_agent` `@agent_tool` on `Diagnose` (separate hop when invoked).
- `transform`, `render` — listed in manifest; hop only when agent chooses format conversion outside lifecycle prose.

**Already in-process / inlined:**
- `super().guidance()` — contexts/examples/templates inlined.
- `generate_output()` — plain method during `/generate` expand (empty default).
- `ce().transform()` — plain delegate if called from `transform` body at runtime (one `@agent_tool` hop for `transform`, not two).

### Target

**leave** — CE companion hop is intentional (`mode=tool`). `diagnose` is agent-chosen after 2 failed fixes.

---

## context_tools/clean_engineering/clean_engineering.py — `CleanEngineering`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `guidance`, `generate_output` |
| `@agent_tool` | `transform`, `render` |

**CLI:** `/clean-engineering`; `/generate` + CE host; drawio path via `generate_output`.

**After first expand — separate hops:**
- `generate_output` when `format=drawio` (expander on `generate_output`): `create_diagram`, `scan`, `repair` — from composed `Drawio.render` inlined into `generate_output` walk (`drawio.mode=tool` defers `repair` sub-agent).
- `transform`, `render` — when agent invokes directly.

**Already in-process / inlined:**
- `guidance` — inlines `super().guidance()`; no companion deferral on CE itself.
- Channel parse/render inside `transform`/`render` `@agent_tool` bodies — single hop each.

### Target

**2A — `drawio_render_pipeline`** (on `Drawio` or CE): swallow `create_diagram` + `scan` + optional `repair` launch into one `@agent_tool` when the agent is not choosing among them — mechanical create→scan→repair sequence for drawio generate. Keep `repair` as sub-agent inside that coarse tool, not a separate listed hop.

**leave** — `transform` / `render` when agent picks format (real choice).

---

## context_tools/ux/ux.py — `Ux`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `guidance` |
| `@agent_tool` | `transform`, `render`, `ensure_javascript` |

**CLI:** `/ux`; lifecycle hosts same as Stories.

**After first expand — separate hops:**
- `transform`, `render`, `ensure_javascript` — only when agent invokes (manifest tools).
- None on `guidance` expand alone.

**Already in-process / inlined:**
- `guidance` → `super().guidance()`.
- `ensure_javascript` calls `Stories().transform` or `CleanEngineering().transform` inside one tool body (single hop).

### Target

**no flatten** — no mechanical multi-hop sequence beyond optional direct tool use.

---

## context_tools/bdd/bdd.py — `Bdd`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `guidance` |
| `@agent_tool` | `transform`, `render` |

**CLI:** `/bdd`; `/generate` + Bdd host.

**After first expand — separate hops:**
- `guidance` on CE companion (`('guidance',)` — same pattern as Stories/Ddd).
- `diagnostic().diagnose()` — agent-invoked sub-agent when stuck.
- `transform`, `render` — delegate to CE inside one `@agent_tool` body.

**Already in-process / inlined:**
- `super().guidance()` + `ce().guidance()` deferral only (not inline CE prose).

### Target

**leave** — CE companion and diagnose are judgment boundaries.

---

## context_tools/ddd/ddd.py — `Ddd`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `guidance` |
| `@agent_tool` | `apply_document_workspace_default`, `transform`, `render` |

**CLI:** `/ddd`; `/document` may call `apply_document_workspace_default` before scan.

**After first expand — separate hops:**
- `guidance` on CE companion (`('guidance',)`).
- `apply_document_workspace_default`, `transform`, `render` — when agent/tool list names them.
- `diagnostic().diagnose()` — agent choice.

**Already in-process / inlined:**
- `transform`/`render` call `ce().transform` inside `@agent_tool` (one hop).
- `scanner` on Ddd uses `Scan` kit at runtime via validate/document prose, not Ddd-local `@agent_tool`.

### Target

**2B — prelude on `/document`:** run `apply_document_workspace_default` in-process before `Document.document` expand when Ddd is in `tools` and path unset — not a separate agent hop.

**leave** — CE `guidance` deferral.

---

## context_tools/create_context_tool/create_context_tool.py — `CreateContextTool`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `guidance` |
| `@agent_tool` | *(none)* |

**CLI:** `/create-context-tool` → `guidance`; `/generate` + this host.

**After first expand — separate hops:** none from this kit alone.

**Already in-process / inlined:** `super().guidance()`.

### Target

**no flatten**

---

## context_tools/agent_bdd/agent_bdd.py — `AgentBdd`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `guidance`, `generate_output` |
| `@agent_tool` | *(none)* |

**CLI:** `/agent-bdd`; `/generate` calls `generate_output` on host.

**After first expand — separate hops:**
- `generate_output` body references `Generate().generate(tools=[self._bdd()])` — **inlined** nested generate recipe in expand prose, but agent must still run **`/generate` on Bdd** as a **cross-toolset action hop** (not listed in AgentBdd expand `tool_steps` — unlisted handoff).

**Already in-process / inlined:**
- `guidance` → `super().guidance()`.

### Target

**2A — `generate_via_bdd`** on `AgentBdd`: one `@agent_tool` that runs `Generate.generate` in-process for `self._bdd()` (swallow separate Bdd remanifest + generate expand hop). Agent still authors specs from inlined guidance.

---

## context_tools/actions/lifecycle.py — `LifecycleAction`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `begin`, `end` |
| `@agent_tool` | `open_workspace` |

**CLI:** `/open-workspace` → `open_workspace`; all host actions call `begin`/`end` in recipe bodies.

**After first expand — separate hops:**
- `open_workspace` — when agent uses `/open-workspace` directly.
- When `begin`/`end` expand **standalone**: nested `record_decisions_session` tools (`read_cdr_format`, `list_cdrs`, `write_cdr`) merge only if `_session()` resolves; often fails silently in expand without open session.
- When inlined into `/generate`, etc.: **no listed hops** from `begin`/`end` themselves; SessionLog.append runs **in-process** during parent expand.

**Already in-process / inlined:**
- `begin` / `end` recipes inlined into every lifecycle `@agent_instructions` outer action.
- `SessionLog.instance().append(...)` in Generate/Validate/… — executed during expand (`_walk_session_log_append`).

### Target

**2B — framework prelude/postlude:** CLI `run` executes `begin` → action expand → `end` + `SessionLog.append` in one process without agent-visible hops. Swallow: `open_workspace` (when session name already known), `Turn.open` binding, `record_decisions_session` prelude (optional), `Turn.finish_turn` postlude. Outer `@agent_instructions` recipes drop explicit `self.begin()` / `self.end()` / `SessionLog.append` lines.

---

## context_tools/actions/generate/generate.py — `Generate`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `generate`, `add_generate_header_to_generated`, `generate_output`, `generate_fixes_from_validate` |
| `@agent_tool` | *(none)* |

**CLI:** `/generate` → `action: generate` on `generate.generate:Generate` with `arguments.tools`.

**After first expand — separate hops (expander `tool_steps`):** `[]`

**Unlisted hops the agent still performs:**
- Author artifacts from inlined `tool.guidance` + `tool.generate_output()` prose (no remanifest if same toolset; **remanifest** when inner recipe points at different toolset).
- `/finish-turn` → `Turn.finish_turn` (separate toolset manifest).

**Already in-process / inlined:**
- `begin`, `end`, `add_generate_header_to_generated`, `generate_fixes_from_validate` — nested actions inlined.
- `tool.guidance`, `tool.generate_output()` — inlined per host (`mode=action`).
- `SessionLog.append` — in-process during expand.

### Target

**2B — pair with lifecycle prelude:** no agent hop for begin/end/log (see LifecycleAction).

**leave** — artifact authoring stays agentic; no coarse tool swallowing `guidance` (agent judgment).

---

## context_tools/actions/validate/validate.py — `Validate`, `CreateRule`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `Validate.validate`, `CreateRule.createRule` |
| `@agent_tool` | *(none)* |

**CLI:** `/validate`, `/createRule`.

**After first expand — separate hops:** `[]`

**Unlisted hops:**
- Agent runs scanners / reads violations from prose (`tool.scanner.scan()` is **not** a listed hop — `Scan.scan` is `@agent_tool` on composed `self.scanner` but referenced as `tool.scanner.scan()` cross-instance inside for-loop → **not emitted** in expander `tool_steps`; agent must discover).
- `/finish-turn` optional.

**Already in-process / inlined:**
- `begin`, `end`, `tool.contexts`, `SessionLog.append`.

### Target

**2A — `run_validate_scan`** on `Validate`: one `@agent_tool` calling `tool.scanner.scan(paths)` for each host (swallow unlisted scan hop).

**2B — lifecycle prelude** (shared).

**leave** — `createRule` authoring (agent invents rule + scanner).

---

## context_tools/actions/satisfy/satisfy.py — `Satisfy`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `satisfy` |
| `@agent_tool` | *(none)* |

**CLI:** `/satisfy`.

**After first expand — separate hops:** `[]`

**Unlisted hops:**
- Inlined `Validate().validate(tools=[tool])` — full validate recipe in prose; agent may re-run `/validate` as separate action hop.
- Fix authoring from `tool.generate_fixes_from_validate()`.

**Already in-process / inlined:**
- `begin`, `end`, nested validate expand, `SessionLog.append`.

### Target

**2A — `satisfy_validate_and_fix`** (optional): run validate scan pass in-process then expand fixes prose only — swallow redundant second `/validate` manifest when satisfy already implies validate.

**2B — lifecycle prelude.**

---

## context_tools/actions/document/document.py — `Document`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `document` |
| `@agent_tool` | *(none)* |

**CLI:** `/document`.

**After first expand — separate hops:** `[]`

**Unlisted hops:**
- `tool.scanner.scan(paths)` — same for-loop gap as validate.
- Ddd: `apply_document_workspace_default` when documenting Ddd artifacts.

**Already in-process / inlined:**
- `begin`, `end`, contexts/templates/generate_output instructions, `SessionLog.append`.

### Target

**2A — `run_document_scan`** — batch scan for all hosts (with Ddd workspace default prelude).

**2B — lifecycle prelude.**

---

## context_tools/actions/render/render.py — `Render`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | *(none)* |
| `@agent_tool` | `render` |

**CLI:** `/render` → single `tool: render` (entire action is `@agent_tool`).

**After first expand — separate hops:** none — one `tool: render` runs `begin`, loop `tool.render(...)`, `end` in Python.

**Already in-process / inlined:** full pipeline inside one `@agent_tool` body (already flattened).

### Target

**no flatten** — reference pattern for 2A/2B on other kits.

---

## context_tools/actions/grill_context/grill_context.py — `GrillContext`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `grill`, `grill_with_context` |
| `@agent_tool` | `explore_context_files`, `read_context_file`, `write_grill_answer` |

**CLI:** `/grill` → `grill(tools)`; sketch/iterate call `grill_with_context` in-method.

**After first expand — separate hops:**
- `grill` outer: `[]` (for-loop does not emit nested tools).
- `grill_with_context`: `explore_context_files`, `read_context_file` (expander confirmed).
- `write_grill_answer` — prose Step 5; **not** in `grill_with_context` `tool_steps` (agent must call from instructions).
- Nested `_generate().generate(tools=[host])` inside `grill` — inlined prose; agent still runs generate work / may remanifest Generate.

**Already in-process / inlined:**
- `begin`, `end` in `grill`.
- AskQuestion Steps 3/3a/3b — agentic chat (must stay).

### Target

**2C — `read_context_files`:** batch `paths: list[str]` → one tool (swallow repeated `read_context_file` hops).

**leave** — `explore_context_files` (one call), `write_grill_answer` (per-insight timing), AskQuestion interview.

**leave** — no coarse tool folding AskQuestion into Python.

---

## context_tools/actions/sketch/sketch.py — `Sketch`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `sketch` |
| `@agent_tool` | `find_template`, `save_sketch`, `list_sketches` |

**CLI:** `/sketch`.

**After first expand — separate hops:**
- Expander `sketch`: `[]` (for-loop gap).
- Prose requires: `find_template`, repeated `save_sketch`, inlined `grill_with_context` (with explore/read hops), `_generate().generate` unlisted.

**Already in-process / inlined:**
- `begin`, `end`; `sketch_template` property calls `find_template` at runtime when property read (not expand hop).

### Target

**2A — `sketch_persist_draft`:** optional coarse tool wrapping find_template + save_sketch for first draft (swallow two hops when cadence is mechanical).

**leave** — grill interview multi-turn.

---

## context_tools/actions/iterate/iterate.py — `Iterate`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `iterate` |
| `@agent_tool` | `mark_iterate_tick` |

**CLI:** `/iterate`.

**After first expand — separate hops:**
- Expander `iterate`: `[]`.
- Prose: `mark_iterate_tick`, then generate slice, validate, satisfy — validate/satisfy are **unlisted** cross-action hops inside loop.

**Already in-process / inlined:**
- `grill_with_context` nested expand; `begin`, `end`; `_generate().generate` nested.

### Target

**2A — `iterate_tick`:** one `@agent_tool` recording tick + running host validate scan in-process (swallow `mark_iterate_tick` + unlisted validate hop when slice boundary already approved).

**leave** — grill questions; generate slice authoring; one-fix satisfy judgment.

---

## context_tools/actions/partition/partition.py — `Partition`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `partition`, `partition_corpus` |
| `@agent_tool` | `verify_segment_completeness`, `index`, `segment` |

**CLI:** `/partition` → `partition(tools, context, …)`.

**After first expand — separate hops:**
- `partition`: `[]` (delegates to `partition_corpus` inline).
- `partition_corpus`: `index`, `segment`, `verify_segment_completeness`.

**Already in-process / inlined:**
- `begin`, `end`, `host.contexts`, `partition_guidance` instruction slot.

### Target

**2A — `partition_corpus_run`:** one `@agent_tool` running index → segment → verify_segment_completeness in Python (swallow three listed hops — agent not choosing among them).

---

## context_tools/actions/improvement/improvement.py — `Improvement`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `repair` |
| `@agent_tool` | `verify_fix` |

**CLI:** `/repair`.

**After first expand — separate hops:**
- `repair`: `[]`.
- Prose directs `diagnose.diagnose:Diagnose` — separate sub-agent hop (agent must choose when stuck).
- `verify_fix` — when agent runs regression check.

**Already in-process / inlined:**
- `repair_loop` instruction, `begin`, `end`, `SessionLog.append`, repair bucket `open` plain calls.

### Target

**leave** — repair diagnosis and kit change are agentic; `diagnose` hop intentional.

---

## utilities/workspace/workspace.py — `Workspace`, `WorkSession`, `Turn`

### Current

| Class | `@agent_instructions` | `@agent_tool` |
|-------|----------------------|---------------|
| `Turn` | *(none)* | `open`, `finish_turn`, `record_mistake`, `record_correction` |
| `WorkSession` | *(none)* | `start_work_session`, `finish_work_session` |
| `Workspace` | *(none)* | `open` |

**CLI:** `/start-turn`, `/finish-turn`, `/mistake`, `/correction`, `/start-work-session`, `/finish-work-session`, `/open-workspace` (via Lifecycle).

**After first expand — separate hops:**
- Each `@agent_tool` above is its own manifest+run when invoked from skills.
- `SessionLog.append` — **not** an agent tool; runs in-process during action expand or via session trail.

**Already in-process / inlined:**
- `Turn.finish` / git commit — called from `finish_turn` body (one hop for `finish_turn`).
- `WorkSession` plain methods (`close_session`, `record_context_root`, …) — called from workflow tools in-process.

### Target

**2B — postlude `finish_turn`:** framework invokes `Turn.finish_turn` after lifecycle actions when session open — swallow separate `/finish-turn` manifest when turn lifecycle is implied.

**2A — `record_mistake_and_correction`:** only if agent routinely chains mistake+correction as mechanical pair (lower priority).

**leave** — `start_work_session` / `open` when agent must confirm slug/path with user.

---

## utilities/workflow/workflow.py — `Workflow`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `backlog` |
| `@agent_tool` | `capture_backlog`, `start`, `finish` |

**CLI:** `/backlog`, `/start-ticket`, `/finish-ticket`.

**After first expand — separate hops:**
- `backlog` expand: `compact_handoff`, `capture_backlog`.
- `start`, `finish` — entire bodies are `@agent_tool` (one hop each); include git/session side effects in-process.

**Already in-process / inlined:**
- `handoff_session` prose in backlog calls `compact_handoff` (listed); turn finish inside `start`/`finish` tool bodies.

### Target

**2A — `backlog_capture`:** one `@agent_tool` = `handoff.compact_handoff` + `capture_backlog` (swallow two hops on `/backlog`).

**no flatten** on `start` / `finish` — already single tool.

---

## utilities/handoff/handoff.py — `Handoff`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `handoff_session` |
| `@agent_tool` | `resolve_working_folder`, `collect_session_state`, `compact_handoff`, `write_handoff` |

**CLI:** handoff prompt; `/backlog` uses `compact_handoff`.

**After first expand — separate hops:**
- `handoff_session`: `compact_handoff` (expander); prose also mentions turn finish (plain in body when session exists).

**Already in-process / inlined:**
- `compact_handoff` internally calls `resolve_working_folder`, `_collect_state`, `_render_handoff_markdown`, `write_handoff` in one `@agent_tool` body when invoked directly.

### Target

**no flatten** on `compact_handoff` — already bundles collect+write. `handoff_session` could **leave** single `compact_handoff` hop.

---

## utilities/sub_agent/sub_agent.py — `SubAgent`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `run` (`@sub_agent`) |
| `@agent_tool` | *(none — sub_agent suppresses tool discovery)* |

**CLI:** `/sub-agent`.

**After first expand — separate hops:**
- Parent launches sub-agent (non-blocking) — not a CLI hop in parent; sub-agent runs listed actions/tools separately.

**Already in-process / inlined:** manifest `kind: sub_agent`.

### Target

**leave** — decomposition is intentional.

---

## utilities/diagnose/diagnose.py — `Diagnose`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | *(docstring on `@agent_tool`)* |
| `@agent_tool` | `diagnose` (`@sub_agent`) |

**CLI:** `/diagnose`; referenced from Stories/Ddd/Bdd/Improvement prose.

**After first expand — separate hops:**
- One sub-agent launch per `diagnose` invoke.

**Already in-process / inlined:** full phase recipe in tool docstring.

### Target

**leave** — agent chooses when to diagnose; sub-agent boundary stays.

---

## utilities/echo/echo.py — `Echo`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `echo_session` |
| `@agent_tool` | `fence` |

**CLI:** echo prompt (diagnostic).

**After first expand — separate hops:** `fence` (expander on `echo_session`).

**Already in-process / inlined:** none.

### Target

**2A — `echo_session_fenced`:** one `@agent_tool` inlining fence (swallow `fence` hop) — diagnostic-only kit.

---

## utilities/git/git.py — `Repo`, …

### Current

No `@agent_tool` or `@agent_instructions` on domain types. Manifest facade only.

**CLI:** none directly; `/start-ticket`, `/finish-ticket`, `/backlog` via `Workflow`.

### Target

**no flatten** — not an agent kit surface.

---

## utilities/scanners/scan.py — `Scan`; `scanner.py` — `Scanner`

### Current

| Kit | `@agent_instructions` | `@agent_tool` |
|-----|----------------------|---------------|
| `Scan` | *(none)* | `scan` |
| `Scanner` | *(none)* | *(none — library)* |

**CLI:** `/scan` → `Scan.scan`; validate/document call `tool.scanner.scan()` (composed on hosts).

**After first expand — separate hops:**
- `scan` when manifest lists it; **unlisted** when only referenced from validate/document for-loop.

**Already in-process / inlined:** scanner collection run inside `scan` body.

### Target

**2A — via Validate/Document** (see above), not a new Scan tool.

---

## utilities/record_decisions/record_decisions.py — `RecordDecisions`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `record_decisions_session` |
| `@agent_tool` | `read_cdr_format`, `list_cdrs`, `write_cdr` |

**CLI:** `/record-decisions-session`; prelude from `LifecycleAction.begin`.

**After first expand — separate hops:**
- `record_decisions_session`: `read_cdr_format`, `list_cdrs`, `write_cdr`.

**Already in-process / inlined:** called from `begin` when session resolves (nested merge).

### Target

**2B — prelude:** run `read_cdr_format` once at session open in-process; agent only hops on `write_cdr` when a decision crystallizes (**leave** write as agent-timed hop).

---

## utilities/catalog_generator/catalog_generator.py — `CatalogGenerator`, …

### Current

No `@agent_tool` or `@agent_instructions`. HTML/catalog builder consumed by Harness and docs.

### Target

**no flatten**

---

## utilities/context_setup/context_setup.py — `ContextSetup`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `capture_from_live_app`, `capture_from_documents` |
| `@agent_tool` | `convert`, `smoke_test`, `scout_app`, `complete_capture` |

**CLI:** `/capture-from-documents`, `/capture-from-live-app`.

**After first expand — separate hops:**
- `capture_from_documents`: `convert`, `embed` (expander); **`stories.partition()` et al. not emitted** (Stories lacks `partition` method — expand error prose; agent directed by Step 3 prose to run `/partition` on selected tools).
- `capture_from_live_app`: `smoke_test`, `scout_app`, `complete_capture`, `embed`.
- Composed tools `stories`, `ddd`, … have `mode=tool` — their `@agent_instructions` would defer if callable.

**Already in-process / inlined:**
- AskQuestion Step 2 — agentic.
- `context_index.embed` via composed `ContextIndex`.

### Target

**2A — `capture_documents_pipeline`:** convert → delegate partition(s) in-process for selected indexers → embed (swallow convert+embed pair and unlisted partition manifests when indexers already chosen).

**leave** — AskQuestion indexer selection; live-app stub authoring steps.

---

## utilities/context_setup/context_index.py — `ContextIndex`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `ask` |
| `@agent_tool` | `embed`, `search` |

**CLI:** `/embed`, `/search`, `/ask`.

**After first expand — separate hops:**
- `ask`: `search`.
- `embed`, `search` when invoked directly.

**Already in-process / inlined:** answer composition prose (agentic).

### Target

**leave** — agent composes cited answer from search results.

---

## primitives/harness/harness.py — `Harness`

### Current

| Kind | Name |
|------|------|
| `@agent_instructions` | `generate` |
| `@agent_tool` | `walk`, `suggested_deploy_path`, `write_deploy`, `generateAgain`, `clean` |

**CLI:** `/deploy-harness`, harness deploy flow.

**After first expand — separate hops:**
- `generate` expand: `suggested_deploy_path`, `write_deploy`.
- AskQuestion prose for IDE/filter/path — agentic.

**Already in-process / inlined:**
- `write_deploy` calls `walk` internally when needed (one hop for write_deploy).

### Target

**2A — `deploy_generate`:** one `@agent_tool` = suggest path + write_deploy (swallow two listed hops after AskQuestion answered).

**leave** — AskQuestion for IDE/path/filter.

---

## primitives/actions/action.py — `ActionExpander` / `AgenticToolset`

### Current

Not a kit — invoke surface behavior:
- Parses `@agent_instructions` bodies → `instructions` + `tools` list.
- Inlines nested `@agent_instructions` unless callee `mode=tool`.
- Emits `@agent_tool` and cross-instance tools as hops.
- Runs `SessionLog.append` and plain calls during expand.
- **Gap:** `for tool in self.context_tools():` bodies do not emit `self.*` or `self.provider().action()` tool steps.

**CLI:** `python -m tools run module:Class --action NAME` / `--tool NAME`.

### Target

**2B — runner hook:** optional prelude/postlude around expand+execute (lifecycle) without agent hops — document only here; implementation is CLI/runner.

**no flatten** of expander itself in this experiment.

---

## primitives/tools/tool.py / cli.py — invoke surface

### Current

Manifest + run; no `@agent_tool` on framework classes.

### Target

**no flatten** (invoke surface only, per scope).

---

## primitives/instructions, focus, assets

### Current

No production `@agent_tool` / `@agent_instructions` outside examples (`recipe_guide`, `review_assistant`, `card_file`). `@focus` appends markdown during expand — in-process.

### Target

**no flatten**

---

## Index — proposed flatten / prelude / batch (method-level)

| Strategy | Proposed name | Swallows / wraps |
|----------|---------------|------------------|
| **2B prelude/postlude** | `LifecycleAction.run_with_session` (runner) | `begin`, `end`, `SessionLog.append`, optional `Turn.open`/`finish_turn`, `open_workspace` when session known |
| **2B prelude** | `Document.document` prelude | `Ddd.apply_document_workspace_default` |
| **2B prelude** | `RecordDecisions` session open | `read_cdr_format` (in-process once) |
| **2A coarse** | `Drawio.drawio_render_pipeline` | `create_diagram`, `scan`, `repair` sub-agent launch |
| **2A coarse** | `Validate.run_validate_scan` | `tool.scanner.scan` per host |
| **2A coarse** | `Document.run_document_scan` | scan + Ddd workspace default |
| **2A coarse** | `Satisfy.satisfy_validate_and_fix` | nested validate scan when redundant hop |
| **2A coarse** | `Partition.partition_corpus_run` | `index`, `segment`, `verify_segment_completeness` |
| **2A coarse** | `Workflow.backlog_capture` | `compact_handoff`, `capture_backlog` |
| **2A coarse** | `Harness.deploy_generate` | `suggested_deploy_path`, `write_deploy` |
| **2A coarse** | `AgentBdd.generate_via_bdd` | cross-toolset `Generate.generate` on Bdd companion |
| **2A coarse** | `ContextSetup.capture_documents_pipeline` | `convert`, partition delegation, `embed` |
| **2A coarse** | `Sketch.sketch_persist_draft` (optional) | `find_template`, `save_sketch` |
| **2A coarse** | `Iterate.iterate_tick` | `mark_iterate_tick` + validate scan |
| **2A coarse** | `Echo.echo_session_fenced` | `fence` |
| **2C batch** | `GrillContext.read_context_files` | repeated `read_context_file` |
| **leave** | — | Grill AskQuestion; CE `guidance` deferrals; Cdd stage children; diagnose/sub-agent; repair invent/map; ContextSetup AskQuestion indexers; ContextIndex.ask; Turn session open when slug unknown |
