# Research — section 3 vs `@agent_instructions` expand runtime

**Session:** optimize-running-context-tools-and-actions-through-the-cli-with-fewer-handoffs-and-fewer-agentic-tool-operations-16  
**Scope:** read-only code research. No implementation. No options 3A/3B/3C applied.

**Question:** Jeff claims nested `@agent_instructions` expand in-process during the first `action:` run; only the first `python -m tools run` with `action:` is a hop. Is section 3 of `options.md` wrong?

**Verdict:** Jeff is correct on the architecture. Section 3 mischaracterizes nested `@agent_instructions` as extra CLI hops and treats 3C (inline nested expand) as future work when `_ActionExpander` already does it. Real follow-on cost is section 2: `@agent_tool` steps the first expand lists for the agent to invoke later, plus section 1 (manifest + file tax).

---

## Context files read first

| Path | Relevant seam |
|---|---|
| `primitives/actions/.context/module-context.md` | `@agent_instructions` bodies parsed via AST, never executed; expand returns instructions + tool list |
| `primitives/tools/.context/module-context.md` | `run` with `action:` expands; `run` with `tool:` executes Python |
| `utilities/workspace/.context/module-context.md` | `SessionLog.append` on expand/run; `Turn.finish_turn` is `@agent_tool` |
| `utilities/workflow/.context/module-context.md` | `backlog` = instructions; `start`/`finish` = one `@agent_tool` each |
| `utilities/echo/.context/module-context.md` | `echo_session` = instructions + deferred `fence` tool |

---

## 1. First `python -m tools run` with `action:` — the hop

### Call chain (one process)

```
cli._ToolsCli._run_main
  → _ToolsetRunner.run_request          (primitives/tools/tool.py)
      → _run_action                     when request has action:
          → ToolsetExtensions.run("action", …)   (primitives/tools/extensions.py)
              → _ActionRunner.invoke_action      (primitives/actions/register.py → action.py)
                  → _ActionExpander.expand       (primitives/actions/action.py)
                  → _build_response              returns YAML payload
```

Evidence:

- `primitives/tools/cli.py` — `_run_main` loads request, calls `_runner.run_request(request)`, prints fenced YAML.
- `primitives/tools/tool.py` — `_ToolsetRunner.run_request` builds instance; if `parsed.action_name`, calls `_run_action` (not `_run_tool`).
- `primitives/actions/action.py` — `_ActionRunner.invoke_action` calls `_ActionExpander.expand`, then `_build_response` with keys `ok`, `toolset`, `action`, `result`, `instructions`, `arguments`, `tools`, `resources`.

### What one expand payload contains

`_ActionExpander._build_expansion_result` returns:

| Field | Source |
|---|---|
| `result` | Return-template string from recipe body (after placeholder substitution) |
| `instructions` | Prose from walked/merged `@agent_instructions` bodies + YAML invoke hint + numbered tool-step list (`_build_instructions`) |
| `tools` | Deduped `@agent_tool` / deferred-action names collected during the walk (`body.tool_steps`) |

Side effects during expand (same process, not a second CLI):

- `_log_expansion` → `SessionLog.append(…, role="expansion")` for every top-level action expand.
- `_walk_session_log_append` → runs `SessionLog.instance().append(…)` when recipe contains that call (e.g. `Generate.generate`).
- `_run_plain_call` → executes unmarked callees during walk (e.g. workspace open side effects when providers resolve).

This matches `primitives/actions/.context/module-context.md`: recipes are read, not executed as Python — except explicit plain-call / SessionLog prelude hooks the expander runs by design.

---

## 2. Nested `@agent_instructions` in a recipe — second CLI or in-process?

**In-process AST merge into the same first payload** (default). Not a second CLI process.

### Expander mechanics

| Function | File | Behavior |
|---|---|---|
| `_walk_body` | `primitives/actions/action.py` | Entry: walks one `@agent_instructions` body; returns `(prose, tool_steps)` |
| `_walk_nested_action` | same | Parses nested action source, calls `_walk_body` recursively, merges into `_ProseAccumulator` |
| `_expand_action_call` | same | If callee `mode == "action"` (default): inline via `_walk_nested_action`. If `mode == "tool"`: append action name to `tool_steps` + deferred-hint prose (`_deferred_action_hint`) — agent must run a **later** `action:` |
| `_walk_super_statement` | same | Empty-body / `super()` delegation: inlines parent `@agent_instructions` body |
| `_walk_cross_instance_statement` | same | `self.<provider>().<member>()` on another toolset: inline nested `@agent_instructions` or list `@agent_tool` on target |
| `_walk_for_each_statement` | same | `for tool in self.context_tools(tools): tool.<action>()` — resolves live instances, inlines per item |

`AgenticToolset.mode` (`primitives/actions/action.py`, `AgenticToolset` docstring): **`action`** = expand inline; **`tool`** = defer to a separate tools-run step.

### Generate → domain tool (the case section 3 cares about)

`context_tools/actions/generate/generate.py` — `Generate.generate`:

```python
self.begin(tools, action="generate")          # same-kit @agent_instructions → inline
for tool in self.context_tools(tools):
    tool.guidance                             # see gap note below
    tool.generate_output()                    # @agent_instructions on subclass → inline when called with ()
    self.generate_fixes_from_validate()       # same-kit nested action → inline
    self.add_generate_header_to_generated()   # same-kit nested action → inline (prose returned, not a hop)
    SessionLog.instance().append(…)           # plain call → runs during expand
self.end()                                    # same-kit @agent_instructions → inline
```

`context_tools/base/base_context_tool.py` — `guidance` is `@agent_instructions`; body references `@instruction` slots (`contexts`, `examples`, `templates`) which `_walk_self_member_statement` inlines via `_inline`.

**Empirical check:** With an open work session, replacing `tool.guidance` with `tool.guidance()` in the walk causes full `# Contexts` prose from `car_chronicle.md` to appear in the merged instructions in the **same** expand (no second CLI). Tool list then includes CDR tools from inlined `begin` → `record_decisions_session` and `finish_turn` from inlined `end`.

### Parent MRO empty-body delegate

`_is_empty_action_body` + `_walk_super_statement`: an empty `@agent_instructions` on a subclass expands the parent's body in the same walk (documented in `_ActionExpander._is_empty_action_body`).

### Explicit opt-out: CDD sets `mode = "tool"`

`context_tools/cdd/cdd.py` — `Cdd.guidance` sets `context_tool.mode = "tool"` before `context_tool.guidance()`. Expander then **defers** each stage child's guidance to a separate `action:` run (`_expand_action_call` lines 827–830). That is intentional cross-hop behavior, not the default.

---

## 3. When a second CLI hop actually happens

A **new** `python -m tools run` (or equivalent shell invocation) is required when:

| Trigger | Mechanism | Evidence |
|---|---|---|
| **`tool:` in request** | `_ToolsetRunner._run_tool` → `_invoke_tool` → executes `@agent_tool` body | `primitives/tools/tool.py` |
| **New top-level `action:`** | Another `_run_action` → full expand (even same toolset) | `cli.py` / `tool.py` |
| **Deferred nested action (`mode=tool`)** | First expand lists action name + hint; agent runs separate `action:` on named toolset | `_expand_action_call`, `_deferred_action_hint` |
| **`@sub_agent` tools** | Listed as tool steps; resolved in `_resolve_runnable` via `ToolsetExtensions.members("sub_agent")` | `tool.py` |

What is **not** a second CLI hop:

- Nested `@agent_instructions` with default `mode=action` (inline walk).
- `@instruction` slot references (`self.contexts`, etc.) — prose inlined.
- `@resource` references — value + docstring inlined (`_describe_resource`).
- Plain prelude calls during expand (`SessionLog.append`, workspace open when resolvable).
- Cross-toolset **load** during expand (`AgenticToolset.context_tool` uses `_ToolsetLoader` in-process) — loading ≠ running a second expand.

**Manifest** (`python -m tools manifest`) is a separate process (section 1), not an `@agent_instructions` nested hop.

---

## 4. What `options.md` section 3 gets wrong (line by line)

Section reference: `.context/sessions/…/options.md` lines 146–175 (+ related 7f, 291–292, 326).

### Heading and premise (146–148)

> “Agentic tool with multiple tools that could be one”

**Wrong framing.** Multiple `@agent_instructions` in one recipe do not imply multiple CLI hops. The expander merges them. The expensive part is `@agent_tool` steps listed in `response.tools` for the agent to run afterward (section 2).

### Cost map cross-reference (lines 48–49, 68)

| Claim in options.md | Runtime truth |
|---|---|
| “Cross-toolset hop — Generate → `tool.guidance` / `generate_output` on Stories” | **Wrong as a default hop.** With `mode=action`, nested `@agent_instructions` on loaded context tools expand in the same walk. CDD explicitly uses `mode=tool` to *create* separate guidance runs. |
| “Empty expansion tool lists … walker does not emit them” | **Overstated.** Tables at lines 60–66 count only top-level recipe `@agent_tool` calls in static parse. Resolved expand with open session inlines `begin` → `RecordDecisions.record_decisions_session` and emits `read_cdr_format`, `list_cdrs`, `write_cdr`, `finish_turn` in `tools` (`utilities/record_decisions/record_decisions.py` nested from `lifecycle.begin`; `lifecycle.end` → `_turn().finish_turn`). Without open session, provider resolution fails and lists stay empty — session/context setup issue, not missing 3C. |
| “unlisted cross-kit work … agent rediscovers with more manifests” | **Partially wrong for `@agent_instructions`.** Cross-kit `@agent_instructions` are designed to inline. Agent remanifesting usually means `@agent_tool` steps or skills/harness habit (section 1/5), or `mode=tool` deferral. |

### Table “Could be one tool” (152–158)

| Row | Section 3 claim | Evidence |
|---|---|---|
| Harness.generate | “AskQuestions then two tools” | `Harness.generate` expands; lists `suggested_deploy_path`, `write_deploy` as `@agent_tool` steps — one expand hop, then agent runs tools (section 2). Not multiple instruction hops. |
| Workflow.start/finish | “already one `@agent_tool` — good pattern” | **Correct.** `workflow.py` — `start`/`finish` are `@agent_tool`; Python runs chain in one `tool:` invoke. |
| Generate.generate | “begin/guidance/output/end → one host tool” | **Misdiagnosed.** `begin`/`end`/nested actions are already inlined by expander. Promoting to `@agent_tool` (3A) would **add** CLI hops, not remove them. |
| Lifecycle begin/end | “one prelude tool” | **Wrong direction.** They are `@agent_instructions` and already merge into first expand. `SessionLog.append` in generate recipe already runs at expand time. |
| Echo.echo_session | “already close to one prompt” | One `action:` expand; `self.fence()` becomes a listed `@agent_tool` step — section 2, not 3. |

### Option 3A (164–165) — promote host actions to `@agent_tool`

**Wrong for hop reduction.** `@agent_instructions` → expand (no Python execution). `@agent_tool` → new `tool:` run executes Python. Converting deterministic recipe steps like `add_generate_header_to_generated` (returns a string template for the agent) or inlined `begin`/`end` prose into tools **increases** CLI invocations.

Workflow `start`/`finish` work as one tool because the **entire chain is Python** in one `@agent_tool` body — that is a different pattern from recipe expansion.

### Option 3B (167–168) — instructions only for choice points

Policy suggestion, not a hop diagnosis. Grill interview should stay `@agent_instructions`; that does not mean other `@agent_instructions` currently cause extra CLI processes — they do not, unless deferred via `mode=tool`.

### Option 3C (170–173) — nested action expand in-process

**Already implemented.** `_walk_nested_action`, `_expand_action_call`, `_walk_cross_instance_statement`, `_walk_for_each_statement`, `_walk_super_statement` in `primitives/actions/action.py`. BDD expectations in `utilities/workspace/workspace_session_spec.py` and `context_tools/base/base_context_tool_spec.py` assert merged prose/tools from `Generate.generate` over context-tool hosts in one `_ActionRunner.invoke_action` call.

**Impact/risk row (310)** — “3c inline nested expand | yes processes | M” — **false premise**; no new M effort needed for inline nested `@agent_instructions`.

### Related 7f (291–292)

> “guidance … each can become another `action:` expand. Option: guidance is text in the first Generate response (3c)”

**Already the default** when nested actions are invoked as calls and `mode=action`. Separate `action:` only when author sets `mode=tool` (CDD) or agent/skills start a new top-level `action:` on another kit.

### Suggested order item 3 (326)

> “inline `guidance` prose into the first generate/validate expand. (2b, 3c, 7f, 7g)”

**3c/7f already done** for inline `@agent_instructions`. Remaining work is elsewhere: session open so `begin`/`end` resolve (`path`/`session` context), author spelling `tool.guidance()` vs bare `tool.guidance` (see gap), and section 2 tool steps.

---

## 5. Hops that look like section 3 but are actually section 2

These appear after the first expand because they are **`@agent_tool` steps** (or deferred `mode=tool` actions), not because nested `@agent_instructions` failed to merge.

| Step | Why it is section 2 | Typical toolset for invoke |
|---|---|---|
| `finish_turn` | Listed from `lifecycle.end` → `_turn().finish_turn()` cross-call; `@agent_tool` on `Turn` | `workspace.workspace:Turn` (name only in Generate kit `tools` list — agent/skills must target correct toolset) |
| `read_cdr_format`, `list_cdrs`, `write_cdr` | Inlined from `begin` → `record_decisions_session`; tools on `RecordDecisions` | `record_decisions.record_decisions:RecordDecisions` |
| Domain `@agent_tool` from `generate_output` override | e.g. `ChronicleWithOutput.generate_output` → `self.add_epic()` | Host context tool |
| `capture_backlog` | `Workflow.backlog` expand lists tool; handoff action inlined | `workflow.workflow:Workflow` |
| `suggested_deploy_path`, `write_deploy` | `Harness.generate` expand | `harness.harness:Harness` |
| `fence` | `Echo.echo_session` expand | `echo.echo:Echo` |
| Grill `explore` / `read` / `write_grill_answer` | Fine tools by design | Grill kit |
| CDD stage `guidance` | **Deferred** via `mode=tool` | Each stage child toolset |

Experiment note (`experiment-baseline-results.md`): first `action: generate` on Generate kit; empty `tools` without session context; agent used separate Stories `action: guidance` — skill/catalog workaround, not proof that expander cannot merge.

---

## 6. Implementation gaps (not section 3 — author/walker spelling)

Separate from Jeff's claim; worth recording so section 3 is not "fixed" in the wrong place.

| Issue | Evidence |
|---|---|
| `generate.py` uses bare `tool.guidance` (no `()`) | `_walk_for_each_body` only handles `var.member()` **Calls** (`_member_call_attr`). Bare attribute access is skipped. Contexts/examples/templates **do not** inline until spelled `tool.guidance()`. Verified: `ctx inlined False` with current source; `True` with `tool.guidance()`. |
| Same for `validate.py` `tool.contexts` | Instruction slots need call form or a walker enhancement for bare attributes. |
| `BaseContextTool.generate_output` is plain Python | Not walked in for-loop unless subclass overrides with `@agent_instructions` (see `chronicle_with_output.py`). Default domain output is agent-written, not a nested expand step. |

`cdd.py` correctly uses `context_tool.guidance()` with parentheses (and intentionally sets `mode=tool`).

---

## 7. Evidence summary table

| Runtime event | Processes | Code anchor |
|---|---|---|
| First `run … --action generate` | 1 | `cli.py` → `tool.py::_run_action` → `action.py::_ActionRunner.invoke_action` |
| `self.begin` / `self.end` in same recipe | 0 additional | `action.py::_expand_action_call` → `_walk_nested_action` |
| `tool.guidance()` with `mode=action` | 0 additional | `action.py::_walk_for_each_statement` → `_expand_action_call` |
| `tool.guidance()` with `mode=tool` | +1 per deferred action (agent) | `action.py::_expand_action_call` lines 827–830 |
| `@agent_tool` listed in `response.tools` | +1 per agent invoke | `tool.py::_run_tool` |
| `python -m tools manifest` | +1 (section 1) | `cli.py::_manifest_main` |

---

## 8. Conclusion for session deferral

**Defer section 3** as Jeff suggested. The expander already implements nested `@agent_instructions` inline expansion (what 3C proposed). Section 3 incorrectly:

1. Treats nested instructions as extra CLI hops.
2. Proposes 3C as new work.
3. Proposes 3A (promote to tools) as hop reduction — opposite of runtime semantics.

**Active cost buckets:** section 1 (manifest + `_req.yaml` + double import), section 2 (`@agent_tool` steps after expand, including `finish_turn` and CDR tools), and author spelling/session context gaps — not missing nested expand machinery.
