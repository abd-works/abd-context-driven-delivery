# Event log consolidation — research

**Date:** 2026-09-06  
**Status:** research only. No production logging code changed.  
**Question:** How can abd-cdd consolidate today's fragmented logs into one (or a small number of) parseable log file(s) that support different fidelity levels for observability and auditability — and what should a new `@event` decorator look like?

User design sketch (not implemented): annotate operations with `@event` (distinct from retired `@log`); event records carry input, output, and op name — not internals; classes may override `to_log()` for richer detail when needed.

---

## 1. Locked decisions from eval-consolidate-workspace

Primary source: `.sessions/closed/eval-consolidate-workspace/workspace-eval-oo-sketch.md`.

| Decision | Detail | Source |
|---|---|---|
| Logging is **not** a decorator | Delete `@log`, `is_logged`, `member_is_logged`, runner log branches | sketch:207–208, 242, 249 |
| Only `@agent_instructions` / `@agent_tool` for author annotations | No `@action`, `@tool`, `@plain_operation` aliases | sketch:199–205 |
| **SessionLog** stays its own class in workspace package | Do not fold into `WorkSession` | sketch:216–217, 704 |
| Two logging moments for auditable `@agent_instructions` | **expand** (framework) + **run** (explicit author `SessionLog.append`) | sketch:218–224 |
| Same record shape everywhere | `toolset`, `name`, `summary`, `ok`, `error`; optional `role=expansion\|run`; optional `payload` | sketch:236–237 |
| Dual write | Every `SessionLog.append` → `events.log` **and** `openTurn.toolCalls` when turn open | sketch:240–241 |
| Retire `control` / `log_full` lines | No `kind=control` filter semantics | sketch:242 |
| Mistake/correction **not** in SessionLog | Git notes + commit trailers | sketch:636, 704 |
| Refactor checklist item 9 | Keep SessionLog; extend ToolCall with `ok`, `error`, `role` | sketch:849 |

Expand vs run call sites (locked):

```
// expand (framework — action expand path)
-> SessionLog.append(toolset, name, summary=expanded_steps, ok=true, role=expansion)

// run (author — end of recipe body)
-> SessionLog.append(toolset, name, summary, ok, error=..., role=run, payload=...)
```

(sketch:228–233)

---

## 2. Current logging landscape

### 2.1 Session operational trail — `events.log`

**Sink:** `{working_path}/.context/sessions/{name}/logs/events.log`  
**Lifecycle:** Grows during session; on close, `consolidate_logs_for_close` moves hook logs into session folder, then the whole session folder archives to `{repo_root}/.sessions/closed/{name}/` including `logs/events.log` (`workspace_session_spec.py:918–936`). `events.log` is gitignored and excluded from dirty checks (`git.py:899–903`, `module-context.md:113`).  
**Parseability today:** Space-separated `key=value` tokens per line — semi-structured, not JSON. Summaries are unquoted and may contain spaces, breaking naive parsers (`session_log.py:261–288`).

**Two writers hit the same file:**

| Writer | Who calls it | Format notes |
|---|---|---|
| `SessionLog.append` | Framework `_log_expansion`; explicit author calls in lifecycle kits; `@agent_tool` bodies (e.g. `LoggedProbe.ping`); expand-time plain-call execution of `SessionLog.instance().append(...)` in recipes | Optional `kind=` prefix; optional `role=`; optional `payload=` ref (stubbed) |
| `WorkSession.append_trail` | `ContextToolHost.ask_for_instructions`, `ContextToolHost.finish` | No `kind=`; includes `role=` when set |

```168:210:utilities/workspace/session_log.py
    def append(
        self,
        *,
        toolset: str,
        name: str,
        summary: str,
        ok: bool,
        ...
    ) -> None:
        ...
        with (self.log_dir / "events.log").open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")
        ...
        self._mirror_to_open_turn(...)
```

```2063:2079:utilities/workspace/workspace.py
    def append_trail(self, call: ToolCall) -> None:
        self.trail.append(call)
        ...
        with (log_dir / "events.log").open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
        if self.open_turn is not None:
            self.open_turn.tool_calls.append(call)
```

**Binding:** On `WorkSession.open`, `_bind_session_log` calls `SessionLog.instance().bind(self)` (`workspace.py:1161–1165`, `1646–1647`). `_ToolsetRunner.run_request` calls `SessionLog.instance().set_session(parsed.session)` per CLI request (`tool.py:351–355`).

**In-memory mirror:** `SessionLog._mirror_to_open_turn` and `append_trail` both append `ToolCall` to `openTurn.tool_calls` (`session_log.py:212–236`, `workspace.py:2078–2079`). Turn git notes store a truncated `tool_calls` string on commit (`workspace.py:369–382`).

### 2.2 Verbose payload side files (stubbed)

`SessionLog._maybe_write_payloads` always returns `None` — companion `event-NNN-request.yaml` / `event-NNN-response.yaml` files are **not written** despite `_write_payload_files` and `last_payload` tracking existing (`session_log.py:238–258`, `241–245`). Authors pass `payload={"request": ..., "response": ...}` (e.g. `logged_probe.py:22–28`) but only `last_payload` in memory is updated.

### 2.3 Prompt / IDE wire audit — `prompt-log.txt`

**Sink:** `.context/sessions/{name}/logs/prompt-log.txt` (via `session_log_path`)  
**Writer:** `primitives/hooks/prompt_log/prompt_log.py` — Cursor hooks: `beforeSubmitPrompt`, `beforeReadFile`, `preToolUse`, `subagentStart`, `afterAgentResponse`  
**Format:** Human-readable blocks with `===` headers, timestamps, previews (8 lines / 600 chars)  
**Lifecycle:** Session-scoped; legacy repo-root `.context/prompt-log.txt` moved on close (`session_logs.py:13–18`, `94–127`)  
**Parseability:** Low — prose blocks, not machine-first.

```4:8:primitives/hooks/prompt_log/prompt_log.py
Appends to ``.context/sessions/{name}/logs/prompt-log.txt`` on:
- beforeSubmitPrompt — user prompt + rule/file attachments
- beforeReadFile — file content Cursor sends to the model
- preToolUse — tool calls (Task prompts, Read paths, shell, etc.)
- subagentStart — subagent task descriptions
```

### 2.4 Hook dispatch debug — `dispatch.debug`, `skill_inject.debug`

**Sink:** `.context/sessions/{name}/logs/dispatch.debug` (and `skill_inject.debug`) via `_hook_debug_path` (`dispatch.py:25–28`, `178–179`, `332–334`)  
**Writer:** `primitives/hooks/dispatch.py` — hook routing diagnostics  
**Format:** Plain text lines (`ENTRY`, `ENABLED`, `MERGED`, etc.)  
**Lifecycle:** Legacy paths under `primitives/hooks/` consolidated on session close (`session_logs.py:15–18`)  
**Parseability:** Low — debug prose.

### 2.5 Manifest gate — `manifest_gate.log`

**Sink:** `utilities/manifest_hook/manifest_gate.log` (package-local, **not** session-scoped)  
**Writer:** `manifest_gate._log` on each hook fire/skip (`manifest_gate.py:51`, `93–103`)  
**Format:** `{ts} [{mode}] {FIRED|skip}  {path}  - {detail}`  
**Parseability:** Medium — fixed columns, single file for all sessions.

### 2.6 CLI agent — `cli-agent-session.jsonl` + role spawn logs

**Sinks (session folder):**

| File | Writer | Format |
|---|---|---|
| `cli-agent-session.jsonl` | `_CliAgentLog.append` | JSONL — `kind`, `ts`, `ts_ms`, `since_last_s`, job/spawn/verdict fields |
| `cli-agent-doer.log` / `cli-agent-judge.log` | `_CliSpawner.append_log` | Text blocks `--- spawn {stamp} ---` + argv |
| `cli-agent.json`, job queue, task txt files | CliAgent lifecycle | Config / prompts — not event stream |

```576:659:utilities/cli_agent/cli_agent.py
class _CliAgentLog:
    """Append-only event log for a cli-agent session: cli-agent-session.jsonl."""
    ...
    def append(self, work, record: dict) -> None:
        ...
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
```

**Parseability:** `cli-agent-session.jsonl` is the most parseable operational log in the repo today. Spawn logs are grep-friendly only.

### 2.7 Agent BDD harness artifacts

**Sinks:**

| Location | Content |
|---|---|
| `{module}/.context/.agent_bdd_sessions/{session}.json` | Session manifest for agent specs (`spec_helpers.py:27`) |
| `{session_file.parent}/logs/{session_file.stem}/instruct-*.md` etc. | Per-instruct artifacts from CLI harness (`agent_cli_bdd.py:60–68`) |
| stdout | `_log_harness` writes `[{name} {ts}] {msg}` to stdout only (`agent_bdd_common.py:288–293`) |

**Not consolidated** with `events.log`. Specs assert on `cli-agent-session.jsonl` via `_agent_bdd_support.records` (`_agent_bdd_support.py:39–51`).

### 2.8 Git-backed audit (durable, not file logs)

| Mechanism | Ref / location | What it stores |
|---|---|---|
| Turn notes | `refs/notes/cdd-turns` | turn_id, context_tool, action, utility, subject, message, tool_calls summary (`workspace.py:254`, `369–382`) |
| Chat notes | `refs/notes/chats` | Chat transcript paths on close (`workspace.py:1736–1741`) |
| Mistake / correction | Git notes on introducing SHA + fix commit trailers | Eval domain — explicitly **not** SessionLog (`sketch:636`, `704`) |
| `context-index.md` changelog | Inline `YYYY-MM-DD: tool = path` lines on upsert (`context_index.py:157–164`) | Path override history — not operation audit |

### 2.9 Dead / stale remnants

| Item | Evidence |
|---|---|
| `@log` decorator | Removed; docs say explicit `SessionLog.append` only (`session_log.py:1–7`). Remaining mentions: BDD style rules (`bdd.md:20`, `49`), eval sketch delete list (`sketch:199–207`) |
| `log_control` in YAML run request | Parsed into `_RunRequest` but never consumed (`tool.py:410–418`, `520`) |
| `_wipe_session_logs` | Defined (`workspace.py:2046–2051`) but **never called** |
| `module-context.md` close step 2 | Says `logs/` deleted via `cleanup` — **stale**; `close()` consolidates and archives logs instead (`workspace.py:1883`, `workspace_session_spec.py:918–936`) |
| `session.yaml` | Spec asserts it is **not** written (`workspace_spec.py:499–505`) |

---

## 3. Who writes SessionLog.append today

### 3.1 Framework expand (automatic)

```1279:1292:primitives/actions/action.py
    def _log_expansion(self, request: _ActionExpandRequest, tool_steps: tuple[str, ...]) -> None:
        """Framework expand append — every @agent_instructions expansion is logged."""
        ...
        SessionLog.instance().append(
            toolset=request.toolset_path,
            name=action_name,
            summary=summarize_mapping({"tools": ",".join(tool_steps)}),
            ok=True,
            role="expansion",
            kind="expansion",
            payload=self._build_expansion_log_payload(request, tool_steps),
        )
```

### 3.2 Expand-time plain-call execution (recipe prelude)

During `@agent_instructions` expand, `SessionLog.instance().append(...)` AST nodes in recipe bodies are **executed** (not deferred to run) via `_walk_session_log_append` (`action.py:1028–1070`). Expand prose records `logged run \`{name}\``.

### 3.3 Author explicit run append (lifecycle kits)

| Module | Method | Summary pattern |
|---|---|---|
| `generate.generate` | `generate` | `"generate"` (`generate.py:30–36`) |
| `validate.validate` | `validate` | `"validate"` (`validate.py:29–35`) |
| `document.document` | `document` | `"document"` (`document.py:30–36`) |
| `satisfy.satisfy` | `satisfy` | `"satisfy"` (`satisfy.py:30–36`) |
| `improvement.improvement` | `repair` | `f"repair {asset}"` (`improvement.py:47–53`) |
| `validate.validate` | `createRule` | `"createRule"` (`validate.py:53–59`) |

Run appends are minimal — mostly static strings, not input/output capture.

### 3.4 Tool-level explicit append

`LoggedProbe.ping` — reference pattern with `summarize_mapping` + `payload` (`logged_probe.py:18–29`). `quiet` / `mute` intentionally omit append (BDD coverage in `session_log_spec.py:110–129`).

### 3.5 Parallel path without SessionLog

`ContextToolHost.ask_for_instructions` → `append_trail` with synthetic expansion record (`workspace.py:2520–2532`). `ContextToolHost.finish` → `append_trail` with `role=run` (`workspace.py:2547–2554`). These bypass `SessionLog` entirely.

---

## 4. Annotation model today (`@agent_tool` / `@agent_instructions`)

```1455:1458:primitives/actions/action.py
def agent_instructions(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as an agent orchestration recipe; body is expanded, never executed."""
    func._is_agent_instructions = True
    return func
```

```691:694:primitives/tools/tool.py
def agent_tool(func: Callable[..., Any]) -> Callable[..., Any]:
    """Mark a method as a tool; instructions come from the method docstring."""
    func._is_agent_tool = True
    return func
```

`session_log.inherit_annotations` copies `_is_agent_instructions` and `_is_agent_tool` markers on subclass overrides (`session_log.py:25–47`) — no logging markers exist.

**Relationship to logging:**

| Annotation | Expand logged? | Run logged? |
|---|---|---|
| `@agent_instructions` | Yes — framework `_log_expansion` | Only if author calls `SessionLog.append` or expand-walks an append in body |
| `@agent_tool` | No (not expanded) | Only if author calls `SessionLog.append` in tool body |
| Plain method | No | No |

There is **no** `@event` or `to_log()` in the codebase (grep: zero matches).

---

## 5. Consolidation options

### 5.1 Single structured log (JSONL recommended)

**Idea:** Replace space-separated `events.log` lines with JSONL (or YAML-lines) where each record is one JSON object.

**Pros:** Machine-parseable; fidelity via nested fields; unifies `SessionLog.append` and `append_trail`; aligns with `cli-agent-session.jsonl` precedent.  
**Cons:** Migration of readers (BDD specs grep `role=expansion` strings); human skim slightly worse unless pretty-print tool exists.

**Suggested record schema (extends locked five fields):**

```json
{
  "ts": "2026-09-06T18:31:00Z",
  "seq": 42,
  "toolset": "context_tools.bdd.bdd:Bdd",
  "name": "generate",
  "role": "run",
  "ok": true,
  "summary": "message=hi",
  "error": null,
  "input": { "tools": ["..."] },
  "output": { "result": "..." },
  "fidelity": "summary"
}
```

`fidelity` enum: `summary` (default — input/output redacted or shortened), `full` (inline or sidecar ref).

### 5.2 Two-tier: summary stream + detail payloads

**Idea:** Activate the stubbed `event-NNN-request.yaml` / `event-NNN-response.yaml` pattern (`session_log.py:247–258`). Summary line in main stream carries `payload_ref=event-042-request.yaml+event-042-response.yaml`.

**Pros:** Matches eval sketch optional `payload`; keeps main log small; full fidelity opt-in per event.  
**Cons:** Two file types to archive; orphan payload files if write fails mid-append; harder to ship as single artifact.

**Current state:** `_maybe_write_payloads` returns `None` always — infrastructure exists but is disabled (`session_log.py:241–245`).

### 5.3 Extend space-separated `events.log`

**Idea:** Keep today's format, add fields.

**Pros:** Minimal diff.  
**Cons:** Already fragile (unescaped summaries); does not solve input/output structure; dual writers still diverge (`kind=` only on one path). **Not recommended** as end state.

### 5.4 What belongs in consolidated log vs stays separate

| Stay separate | Rationale |
|---|---|
| **prompt-log.txt** | Full wire audit (prompts, file reads, tool inputs) — different trust/fidelity contract; large; IDE-hook owned (`prompt_log.py:1–8`) |
| **manifest_gate.log** | Hook delivery diagnostics; not session-scoped (`manifest_gate.py:51`) |
| **dispatch.debug / skill_inject.debug** | Developer hook routing — consolidate location on close only (`session_logs.py:94–127`) |
| **Agent BDD harness artifacts** | Test harness output under `.agent_bdd_sessions/` and per-instruct files — not production session audit (`agent_cli_bdd.py:60–68`) |
| **cli-agent spawn logs** | Low-level argv audit; could merge into JSONL as `kind=spawn` later |
| **Git notes / commit trailers** | Durable correlation (mistakes, turns, chats) — authoritative for eval domain (`sketch:636`, `704`) |
| **context-index.md changelog** | Durable path overrides — not operation stream (`context_index.py:157–164`) |

| Merge into consolidated session event stream | Rationale |
|---|---|
| `SessionLog.append` events | Core CDD tool/action audit |
| `WorkSession.append_trail` events | Same semantic — eliminate duplicate writer |
| **cli-agent-session.jsonl** kinds (optional phase 2) | Already JSONL; same session folder |
| Hook debug (optional, `fidelity=debug`) | Only if observability needs hook routing in one tail |

---

## 6. Proposed `@event` decorator design

### 6.1 Placement

**Module:** `utilities/workspace/session_log.py` (alongside `SessionLog`, `summarize_mapping`) — same package as locked `SessionLog` class; imported by `primitives/actions` and `primitives/tools` via existing `workspace` path bootstrap.

**Not** on `@agent_tool` / `@agent_instructions` themselves — eval sketch locks logging as non-decorator for those (`sketch:207`). `@event` is a **third marker** for *serialization policy*, not agent exposure.

### 6.2 Semantics

```python
@event(role="run", fidelity="summary")  # on @agent_tool methods and plain callables
@event(role="expansion", fidelity="full")  # rarely needed — framework handles expand
```

| Parameter | Default | Meaning |
|---|---|---|
| `role` | `"run"` for tools, inferred for instructions | Maps to locked `role=expansion\|run` |
| `fidelity` | `"summary"` | `summary` → `summarize_mapping` on args/result; `full` → write payload sidecars or inline `input`/`output` |
| `op` | function `__name__` | Locked `name` field |
| `toolset` | `type(self).manifest_path` | Locked `toolset` field |

**On invoke (tool run path):** framework wrapper (in `_ToolsetRunner._invoke_tool` or tool decorator stack) calls `SessionLog.append` with:

- `summary` from `summarize_mapping` of inputs (+ outcome token)
- `payload` / sidecars when `fidelity="full"`
- `ok` / `error` from return value or exception

**On expand:** keep `_log_expansion` as today; `@event` on `@agent_instructions` methods optional for custom expand summary only.

### 6.3 `to_log()` override hook

For classes (typically toolset instances):

```python
class Bdd(BaseContextTool):
    def to_log(self, op: str, *, input: dict, output: Any, ok: bool) -> dict:
        """Return extra fields merged into event record; omit internals."""
        return {"toolset_key": self.context_index_key, "fidelity": self.fidelity}
```

- Default: `to_log` absent → serialize `input` from bound args (respecting fidelity), `output` from return value.
- **Not internals:** default serializer strips private attrs, truncates via `_short` / `summarize_mapping` (`session_log.py:300–314`).
- Class-level override wins over per-method `@event(fidelity="full")` when `to_log` sets `fidelity`.

### 6.4 Relation to `@agent_tool` / `@agent_instructions`

```
@agent_instructions  →  expand path  →  framework _log_expansion (always)
                      →  run append in recipe  →  explicit SessionLog OR @event on plain callees

@agent_tool          →  agent invokes  →  @event wraps run  →  SessionLog.append (replaces hand-written append in tool body)

@event               →  serialization + append policy only; NOT on agent manifest
```

`@event` **replaces** hand-written `SessionLog.instance().append(...)` in lifecycle kits and tools like `LoggedProbe.ping` — not the framework expand hook.

`inherit_annotations` should gain `_is_event` / `_event_fidelity` attrs (parallel to `_INHERITED_MARKER_ATTRS` at `session_log.py:25–28`).

### 6.5 Fidelity levels

| Level | `events.log` / JSONL | Side files |
|---|---|---|
| `summary` | `summary` string + optional typed `input`/`output` keys with truncated values | None |
| `full` | Same summary line + `payload_ref` or inline blobs | `event-NNN-request.yaml`, `event-NNN-response.yaml` via `_write_payload_files` |
| `off` | No append (today: `quiet`, `mute` pattern) | None |

Expand events default `summary` only (tool step list); full expansion payload optional via `@event(fidelity="full")` on the action method.

---

## 7. Gaps and inconsistencies to fix in consolidation

1. **Dual writers** — `SessionLog.append` vs `WorkSession.append_trail` produce slightly different lines and duplicate mirror logic. **Unify** on `SessionLog.append` (or single internal `_append_event`).
2. **Payload stub** — `_maybe_write_payloads` no-op breaks `last_payload` / BDD spec expecting companion files (`session_log_spec.py:93–107`).
3. **Run appends are hollow** — lifecycle kits log static strings, not real input/output (`generate.py:30–36`).
4. **Expand-time run of SessionLog.append** — recipes that append during expand log before run executes (`action.py:1042–1070`) — distinct from locked "run at end of recipe" (`sketch:245`).
5. **module-context.md drift** — close/delete vs archive (`module-context.md:88–89` vs `workspace_session_spec.py:918–936`).
6. **log_control** dead field in runner (`tool.py:410–418`).

---

## 8. Recommendation

### 8.1 Target architecture

**One primary parseable stream per session:** `.context/sessions/{name}/logs/events.jsonl` (keep `events.log` as symlink or phased rename).

- JSONL records with locked fields + `seq` + optional `input`/`output` + `fidelity`.
- **Single writer:** `SessionLog.append` only; deprecate `WorkSession.append_trail` direct file write — trail becomes `self.trail` cache fed by SessionLog.
- **Two-tier fidelity:** default `summary`; `@event(fidelity="full")` or `to_log()` enables sidecar YAML files using existing `_write_payload_files`.
- **Leave separate:** prompt-log, manifest_gate.log, git notes, agent BDD artifacts (section 5.4).

### 8.2 Phased migration

| Phase | Work | Risk |
|---|---|---|
| **P0 — Unify writer** | Route `append_trail` through `SessionLog.append`; one mirror-to-turn implementation | Low — behavior-preserving |
| **P1 — JSONL + schema** | Add `events.jsonl` alongside `events.log`; dual-write during transition; update BDD specs | Medium — update grep assertions |
| **P2 — `@event` on `@agent_tool`** | Framework auto-append on tool invoke; remove manual appends from `LoggedProbe`, lifecycle kits | Medium — fidelity tuning |
| **P3 — Enable payload sidecars** | Implement `_maybe_write_payloads`; wire `fidelity=full` | Low once schema stable |
| **P4 — `to_log()` on hosts** | `BaseContextTool.to_log` for richer run records without internals | Optional |
| **P5 — Retire `events.log` text** | Drop space-separated format; remove `log_control` parsing | Low after consumers migrated |
| **P6 — cli-agent merge (optional)** | Emit cli-agent kinds into same JSONL with `source=cli_agent` | Optional — large surface |

### 8.3 `@event` first implementation slice

1. Add `@event` decorator + `_invoke_with_event_log` in `session_log.py`.
2. Hook `_ToolsetRunner._invoke_tool` for `@agent_tool` methods carrying `@event` (default: all `@agent_tool` get `@event` by default opt-out `@event(off)`).
3. Keep `_log_expansion` unchanged (framework expand).
4. Replace explicit `SessionLog.instance().append` in `generate`, `validate`, `document`, `satisfy`, `improvement` with recipe-level single append or rely on nested tool events — **prefer one run record per action invocation** at kit boundary with `to_log()` on host listing tools processed.
5. Document in `utilities/workspace/.context/module-context.md` after implementation.

---

## 9. Source index

| Topic | Primary file(s) |
|---|---|
| SessionLog API | `utilities/workspace/session_log.py` |
| WorkSession trail / close | `utilities/workspace/workspace.py` |
| Framework expand log | `primitives/actions/action.py` (`_log_expansion`, `_walk_session_log_append`) |
| CLI runner session bind | `primitives/tools/tool.py` (`run_request`) |
| Prompt audit hook | `primitives/hooks/prompt_log/prompt_log.py` |
| Session log paths / close consolidate | `primitives/hooks/session_logs.py` |
| Hook dispatch debug | `primitives/hooks/dispatch.py` |
| Manifest gate log | `utilities/manifest_hook/manifest_gate.py` |
| CLI agent JSONL | `utilities/cli_agent/cli_agent.py` (`_CliAgentLog`) |
| Agent BDD harness logs | `context_tools/agent_bdd/agent_cli_bdd.py`, `agent_bdd_common.py` |
| Locked eval decisions | `.sessions/closed/eval-consolidate-workspace/workspace-eval-oo-sketch.md` §4, §9 |
| BDD specs | `utilities/workspace/session_log_spec.py`, `workspace_spec.py`, `workspace_session_spec.py` |
| Module context (stale close note) | `utilities/workspace/.context/module-context.md` |
