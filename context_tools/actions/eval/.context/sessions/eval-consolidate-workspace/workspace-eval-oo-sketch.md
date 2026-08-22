# Sketch — workspace ↔ eval OO realignment

Session **eval-consolidate-workspace**. CE sources: `context_tools/actions/workspace/.context/workspace-ce.drawio`, `context_tools/actions/eval/.context/eval-ce.drawio`.

---

## 1. Problem

Workspace and eval both use **Session** vocabulary, compose each other through **BaseContextTool** (`_bind_eval`, `repairer`), and split git/logging seams inconsistently — while slash commands invert other kits (`/repair`, `/partition`, …) to **kit owns run, tools are arguments**. The CE diagrams encode extra types (`WorkspaceSession` stub, `Repair` twice) that do not match code.

**Vocabulary (target):** a **workspace** is the folder you chose to work in — the **parent of `.context/`** (not the whole git repo). It owns **many work sessions**, a **`currentWorkSession`**, and a sparse **`pathOverrides`** list. A **context tool** composes **`Workspace`** directly — **`lookupPath`**, **`path`**, overrides — without going through a work session. Turn/git/repair state lives on **`workspace.currentWorkSession`**. **`GitRepo`** is at `find_git_root(...)` — separate from workspace boundary. *Code today: `host.workspace` is a misnamed **`WorkSession`**, not **`Workspace`**.*

**Naming (locked):** **`Workspace`** = parent of `.context/`. **`WorkSession`** = one work session. See §2 rename table for today's Python names.

**No aliases, no legacy (locked):** this refactor does **not** ship compatibility shims, rename aliases, dual decorators, import aliases (`Session = …`), or gradual migration. **One name per concept.** Delete old names in the same pass — do not re-export under a second name. See §4.

---

## 2. Target model — workspace

From `workspace_session.py` + `context_index.py`. **The model below is the domain we want** — not a line-for-line copy of today's Python. CE diagrams are illustrative; **this block is source of truth**. No separate **`ContextIndex`** type — today's `context_index.py` helpers fold into **`Workspace`** load/save/lookup.

**Renames from today's Python** (migration only — not part of the runtime model):

| In this sketch | In code now |
|---|---|
| `Workspace` | no class yet — folder path stored as `Session.workspace_root` |
| `Workspace.workSessions` | folders under `{workspace_root}/.context/sessions/*` — no aggregate yet |
| `Workspace.pathOverrides` | `## Current` rows in `{workspace_root}/.context/context-index.md` — no list on a class yet |
| `WorkSession` | class `Session` in `workspace_session.py` |
| `host.workspace` | target: **`Workspace`** aggregate — code today: property holds a **`Session`** (`WorkSession`) |
| `Workspace.currentWorkSession` | today's current work session on that `Session` object |
| `context_index.py` | delete as a separate domain type — persistence + lookup live on **`Workspace`** |
| `WorkspaceSession` | delete — was an export alias |

**Three levels (locked):**

1. **`Workspace`** — parent of `.context/`; **`pathOverrides`**, **`workSessions`**, **`currentWorkSession`**.
2. **`WorkSession`** — one named work session; owns turns, git, repairs for that bout.
3. **`BaseContextTool.workspace`** — composed **`Workspace`** — paths/overrides **direct**; current work session via **`workspace.currentWorkSession`**.

```
Workspace
  path                                  // parent of .context/
  workSessions: list[WorkSession]        // every work session folder — current and past
  currentWorkSession: WorkSession | None // current work session — set on open
  pathOverrides: list[PathOverride]      // sparse — only when path ≠ host default for (tool, fidelity)
  load() save()
  lookupPath(tool, fidelity) path
  upsertPath(tool, fidelity, path)
  openWorkSession(name, goal, fidelities, contexts, path)
    -> currentWorkSession = load or create in workSessions
    -> load(); currentWorkSession.open(...); upsertPath when ≠ default
  ----
PathOverride                            // one row — not a separate aggregate
  tool: str
  fidelity: str
  path: str                             // folder under Workspace.path (workspace-relative)
  ----
WorkSession
  workspace Workspace                     // back-ref — listed in parent workSessions
  path name folder goal fidelities contexts
  session_branch scope_paths dirty
  git GitRepo                             // find_git_root(workspace.path) — may be above workspace.path
  openTurn Turn | None
  turns list[Turn]
  repairs list[Repair]
  // path = durable tool root for this bout (where generate/validate edit)
  // folder = {workspace.path}/.context/sessions/{name}/
  open(name, goal, fidelities, contexts, path) / close(outcome, handoff) save() load()
  // open: checkout session branch (git on this session)
  ----
GitRepo                                 // at find_git_root(workspace.path)
  root branch current_branch current_commit
  create_branch checkout_or_create commit push is_dirty
  NullGitRepo
  ----
SessionPaths                            // path helpers for a work session
  docs_dir(destination): Path
  ----
SessionLog                              // binds one WorkSession; not composed on it
  bind(workSession) append(...)
  ----
BaseContextTool (each host declares defaults)
  workspace Workspace                     // paths + overrides direct; turn/git via currentWorkSession
  turn Turn
  context_index_key str                   // → PathOverride.tool
  default_workspace_folder str
  // resolved edit path — direct from workspace, not via work session:
  //   1. workspace.lookupPath(context_index_key, fidelity)
  //   2. else {workspace.path}/{default_workspace_folder}
  // turn / git / repairs — via workspace.currentWorkSession
  ----
GitConnectError / DirtyBranchSwitchError
```

**Delete in refactor:** type name `Session`, export `WorkspaceSession`, and every import path that used either name without saying `WorkSession`.

**Relationships**

- **`Workspace.path`** — parent of `.context/`; **`pathOverrides`** persisted at `{path}/.context/context-index.md`; **all `WorkSession` folders** under `{path}/.context/sessions/`
- `Workspace` ◆— `WorkSession` via **`workSessions`** — one or many (open or closed)
- `Workspace.currentWorkSession` → **`WorkSession`** — the **current work session** (must be one of `workSessions`)
- `Workspace.pathOverrides` — **`list[PathOverride]`**
- `BaseContextTool` ◆— **`Workspace`** — paths/overrides **direct** on host
- `WorkSession` ◆— `GitRepo` via `git`
- `WorkSession` ◆— `Turn` via `openTurn`; `turns` holds closed turns
- `WorkSession` ◆— domain `Repair` via `repairs`
- `SessionLog` → binds **`workspace.currentWorkSession`**

### Path overrides (example)

File: **`{workspace.path}/.context/context-index.md`** — just persistence for **`Workspace.pathOverrides`**. Each row is **`tool`, `fidelity`, `path`**. Only include a row when that path differs from the host's `default_workspace_folder` for that fidelity.

| tool | fidelity | path |
|---|---|---|
| `bdd` | `modules` | `./context_tools` |
| `clean_engineering` | `modules` | `./../story-ui` |
| `stories` | `story_map` | `./../story-ui` |

Stories' default folder is `tests`; Bdd's is `src` — so these rows say "for this tool at this fidelity, work here instead."

If everything uses defaults, the file is empty (or omit the file). **No separate change log** — drop today's `## Log` section in refactor.

**Resolution on `open`:**

1. explicit `path` argument
2. else `workspace.lookupPath(context_index_key, fidelity)`
3. else `{workspace.path}/{default_workspace_folder}`

**On `open`:** `workspace.upsertPath(tool, fidelity, path)` when resolved path ≠ default; remove the row when it matches default again. (Today `record_context_root` always writes — tighten in refactor.)

### Workspace leaks

| Issue | Symptom |
|---|---|
| **Duplicate `Session` name** | Work package and eval package both use `Session`; eval also exports `Session = EvalSession`. One word, three meanings. |
| **`workspace_root` vs `path`** | Today: `workspace_root` = **Workspace.path** (parent of `.context/`); `path` = durable tool edit root. CE must not collapse them. |
| **Session does too much** | Lifecycle tools + path/index state + implied git. CE lists git ops on `Session` that belong on `GitRepo` + WorkSession policy. |
| **GitRepo domain leak** | `ensure_session_branch` / `commit_on_session_branch` encode work-session branch naming — belongs on WorkSession. |
| **Git on wrong aggregate** | `commit_on_session_branch` called from **EvalSession.finish_turn**; checkout vs commit not split cleanly. |

---

## 3. Current model — eval

From `eval-ce.drawio` + `eval/session.py` — **target removes EvalSession as turn owner**.

```
EvalSession (delete — turn owner today)
  workspace: WorkSession              // today: Session type in workspace package
  turns, openTurn, mistakes      ← turns move to WorkSession
  repairs: list[Repair]          ← domain runs ⚠ same name as toolset
  begin_turn / finish_turn         ← move to Turn (WorkSession.openTurn)
  ----
  Turn, ToolCall, TurnCommit, Mistake, Correction
  Repair : AgenticToolset          ← bundles record + run ⚠ split → Turn + Improvement
  Archive
```

**Delete in refactor:** `EvalSession`, eval export `Session = EvalSession`, and any type or import that reused `Session` for eval.

**Relationships (diagram)**

- `EvalSession` ◆— `WorkSession` (location — delete EvalSession)
- `EvalSession` → `GitRepo` via domain wrappers (`commit_on_session_branch` ⚠)
- `EvalSession` ◆— `Repair` toolset instances in `_repairs`
- `Repair` → `cddSession`, `Scan`, `BaseContextTool`
- `Turn` ◆— `ToolCall`; `Turn` → `TurnCommit`
- `Mistake` → `Correction` (Correction.add); Mistake → introducing commit SHA; Correction → fix commit SHA

### Eval leaks

| Issue | Symptom |
|---|---|
| **`Session = EvalSession` export** | Import trap — delete; use `WorkSession` and domain types only. |
| **EvalSession owns turns** | Turn lifecycle belongs on **Turn** (`WorkSession.openTurn`); eval package owns mistake/repair domain only. |
| **Two “Repair” types** | Toolset bundles record + run; same name as themed repair bucket — split toolsets and domain **Repair**. |
| **`Repair.eval()` action** | Overloads package/session vocabulary. |
| **Eval on host init** | `_bind_eval()` + `repairer` at construction, not at `open`. |
| **`host.eval` vs `workspace.eval`** | Split attribute; SessionLog uses workspace side. |
| **CDDRepo extends GitRepo** | Eval/repair behavior on repo type — use second `GitRepo(tools_root)` at caller. |
| **Nested EvalSession** | `cdd_session` on CDD clone — no primary vs clone stereotype in CE. |
| **No turn toolset** | `begin_eval_turn` / `finish_eval_turn` on host; target: **Turn** kit owns turn **@agent_tool**s. |
| **CE stub type `WorkspaceSession`** | CE shows `{ path, folder, open }` — `open` is not a field; delete the stub name. |

---

## 4. Target model — aggregate boundaries

Domain chain: **WorkSession → Turn → Mistake → Repair (themed, backlog | finished)**.

**Resource-oriented split:** **Turn** is one class — agentic kit *and* `WorkSession.openTurn`. **Mistake** / **Correction** persist files only (`persist`). **Improvement** owns `/repair`.

### Agent annotations & invoke semantics (target)

**Only two author annotations:** `@agent_instructions`, `@agent_tool`. Everything else is plain Python or framework behavior — not a decorator authors apply.

**No legacy decorators.** Delete `@action`, `@tool`, `@log`, and `@plain_operation` from primitives, manifests, generator output, and docs in the **same** refactor pass. Do not keep them as aliases, shims, or “during migration” re-exports. Framework and runner recognize **`@agent_instructions`** and **`@agent_tool`** only.

| Annotation | Meaning |
|---|---|
| `@agent_instructions` | Recipe body — expand nested steps or run when invoked |
| `@agent_tool` | Agent-invokable tool — listed on manifest; body runs on agent invoke |
| *(none)* | Plain operation — Python callable; runs when a recipe calls it |

**Logging is not a decorator.** Auditable `@agent_instructions` use explicit `SessionLog.append(...)` (run) and framework expand append — see below. Delete `@log`, `is_logged`, `member_is_logged`, and runner log branches entirely.

When an **`@agent_instructions`** recipe is invoked, the framework walks the body. **What happens depends on the callee annotation — not on which class owns the recipe.**

| Callee | Behavior | Agent sees |
|---|---|---|
| Plain method (no annotation) | **run** — execute as Python now; summary in prelude / response | Not on tool list |
| `@agent_tool` | named in recipe; agent invokes (body runs when agent calls it) | Tool on manifest + when-to-use in instructions |
| `@agent_instructions` | **expand** — inline nested recipe (callee `mode="tool"` → defer like a tool step) | Inlined instructions |

**SessionLog stays its own class** in `context_tools/actions/workspace/session_log.py` — do not fold into `WorkSession`, do not move to the host.

**Two logging moments for auditable `@agent_instructions`** (`generate`, `validate`, `document`, `satisfy`, `scan`, `createRule`):

| Moment | Who writes | When |
|---|---|---|
| **expand** | **framework** — on `@agent_instructions` expand | Agent (or slash) asks for instructions; summary lists expanded steps (`contexts`, `examples`, `finish_turn`, …) |
| **run** | **author** — explicit `SessionLog.append(...)` in recipe body | Action body actually executes; summary = run args/outcome |

Both use the same **`SessionLog.append`** path and the same turn scoping (below). **Not** `@agent_tool`.

```
// expand (framework — action expand path)
-> SessionLog.append(toolset, name, summary=expanded_steps, ok=true, role=expansion)

// run (author — end of recipe body)
-> SessionLog.append(toolset, name, summary, ok, error=..., role=run, payload=...)
```

**Record shape (locked):** every `append` carries **`toolset`**, **`name`**, **`summary`**, **`ok`**, **`error`** (optional when success). Same five on **`events.log`** and on **`openTurn.toolCalls`** / **`session.yaml`**. Optional **`role=expansion|run`** on the log line (metadata only — not a filter). Optional **`payload`** (verbose/full) stays session-log-only side files.

**Logging scoping (locked):**

- **One call, same record, both places** — every `SessionLog.append` (framework expand **or** author run) writes **`events.log`** and **`openTurn.toolCalls`** (when turn is open). **Expansion included** — no session-only expansion trail.
- **Log is an operation** — not a `@agent_tool`, not on the agent manifest.
- **Drop invalid kinds from today:** no **`control`**. Delete `apply_log_control` / `log_full` control lines. Delete `@log` / `is_logged` / runner run-branch logging — replaced by explicit run append + framework expand append.
- **`tool` / `action` / `expansion` on `events.log`:** retire as **filters**; optional **`role`** metadata only.

Run append: after prelude, before `return`. Expand append: in action expand path (today `_log_expansion` → unified `SessionLog.append`).

### Fix logging (sketch note — not in this refactor pass)

Remove `@log`, `is_logged`, `member_is_logged`, runner run-branch logging, **`control`** lines. **Keep `SessionLog` as its own class.** **`append` → events.log + openTurn.toolCalls** for both **expand** (framework) and **run** (explicit in recipe).

**Decisions (locked):**

- Any `@agent_instructions` body may **run** plain code — hosts and kits alike.
- Plain code is just code — any callable in the body may run; no receiver whitelist.
- **`self.turn.finish_turn(tools, prompt, result, context)`** — **`@agent_tool`** on **Turn**. Last line in **`generate` / `validate`** recipe. Agent supplies params after work. Not inline `finish_eval_turn` on host.
- **Session prelude** — **`self.workspace.openWorkSession(...)`** — sets **`currentWorkSession`**, loads overrides, opens the work session branch. **`self.turn.open(self)`** — turn on **`workspace.currentWorkSession`**. Both **plain**. *Code today: `self.workspace.open()` on the misnamed WorkSession property.*
- **`Turn.open(host)`** — plain; **opens a turn** for this generate/validate run. Default: new `Turn` on `openTurn` (`finish_turn` cleared it last time). **Edge case only:** if `openTurn` still set (agent never finished — failure/recovery), reuse existing — do not clobber.
- **`Turn.finish` always pushes** — after turn close, **`workSession.git.push()`** runs every time (session branch → `origin`). Commit when dirty first; push regardless so remote always tracks the session branch before the agent moves on.

**Turn envelope (locked):**

```
open turn          -> self.workspace.openWorkSession(...) + self.turn.open(self)   // workspace then turn
agent work         -> domain steps; optional record_mistake / record_correction @agent_tool
close turn         -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work
                      -> openTurn.finish(...)        // commit if dirty; push session branch; openTurn = None
```

**Not gone** — was inline `finish_eval_turn` on host; now **`self.turn.finish_turn(tools, prompt, result, context)`**.

**Generate envelope — on `BaseContextTool` (Bdd, Cdd, …), not a separate orchestrator class:**

```
BaseContextTool.generate @agent_instructions   // /generate → Bdd.generate directly
  -> self.workspace.open()                   // plain — work session: resume or create
  -> self.turn.open(self)             // plain — open turn for this run
  -> self.decisions.record_decisions_session()  // plain
  -> self.contexts                            // expand
  -> self.examples                            // expand
  -> self.templates                           // expand
  -> self.generate_output()                   // expand
  -> self.add_generate_header_to_generated()  // plain
  -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work
```

**Vocabulary:** **host** = `BaseContextTool` subclass (`Bdd`, `Cdd`, …). Lifecycle lives **on the host** — `generate`, `validate`, `document`, `satisfy` are `@agent_instructions` on `BaseContextTool` today and stay there.

**`HostLifecycle`** (`host_lifecycle.host_lifecycle:HostLifecycle`) — interim kit from action-owns-context-tools that only loops `host.generate()`. **Target: delete.** Agent skills route `/generate` to **`context_tools.bdd.bdd:Bdd`** `action: generate` (same as invoke-check), not HostLifecycle.

### Kill `HostLifecycle` (sketch note — not in this refactor pass)

**Why it exists today:** `agent_skills.py` deploy writes kit-owned skill text for `/generate`, `/validate`, `/document`, `/satisfy` — instructing the agent to invoke `HostLifecycle.*(tools=[…])` instead of each host with `action: generate`. The Python class is a ~40-line loop; real lifecycle lives on `BaseContextTool`.

**Why delete:** No orchestration logic — only duplicates what `_CHAIN_TOOLS` already does in host-owned skill text. Misleading name; wrong place in the mental model.

**Multi-tool without it:** `/stories /ddd /generate` stays supported. Host-owned deploy text runs **each** named context tool with `action: generate` in order (sequential invokes). You lose one YAML with `arguments.tools`; you do not lose multi-host generate.

**When implemented (later slice), remove:**

| Area | Action |
|---|---|
| `context_tools/actions/host_lifecycle/` | Delete kit, specs, agent BDD, module-context |
| `utilities/agent_skills/agent_skills.py` | Remove `generate`, `validate`, `document`, `satisfy` from `_KIT_OWNED_INVOKE_BODIES` — use `_ACTION_INVOKE_BODY` (host-owned) |
| `utilities/agent_skills/agent_skills_spec.py` | Drop "generate/validate owns HostLifecycle" examples; assert host `action:` chaining instead |
| `context_tools/actions/.context/module-context.md` | Remove host_lifecycle from kit-owned table |
| `context_tools/base/.context/module-context.md` | Lifecycle slash → host action, not HostLifecycle |
| Redeploy skills | Regenerate `.cursor/commands/generate.md` etc. so agent calls `Bdd.generate()`, not HostLifecycle |

**Keep kit-owned for real orchestrators only:** `iterate`, `sketch`, `grill`, `partition`, `repair` — actions that are not full recipes on `BaseContextTool`.

Host **`generate` / `validate`** — prelude plain run, domain steps, **`self.turn.finish_turn(tools, prompt, result, context)`** in recipe.

**Read top-down:** **`BaseContextTool`** composes **`Workspace`** — paths/overrides direct. **Current work session:** **`host.workspace.currentWorkSession`**. Turn state: **`currentWorkSession.openTurn`**. **`host.turn`** is the Turn kit.

*Pseudocode in §5–§8: **`host.workspace.currentWorkSession`** for turn/git/repairs; **`host.workspace.lookupPath`** for paths. Code today uses misnamed `host.workspace` as the WorkSession itself.*

```
BaseContextTool : AgenticToolset
  workspace Workspace                     // paths + overrides; currentWorkSession for turn/git
  turn Turn
  generate() @agent_instructions
    -> self.workspace.open()                   // plain
    -> self.turn.open(self)             // plain
    -> self.decisions.record_decisions_session()  // plain
    -> self.contexts                            // expand
    -> self.examples                            // expand
    -> self.templates                           // expand
    -> self.generate_output()                   // expand
    -> self.add_generate_header_to_generated()  // plain
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
    -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work
  validate() @agent_instructions
    -> self.workspace.open()                   // plain
    -> self.turn.open(self)             // plain
    -> self.contexts                            // expand
    -> self.scan()                              // expand
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
    -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work
  document(paths) @agent_instructions
    -> self.workspace.open()                   // plain
    -> self.turn.open(self)             // plain
    -> self.contexts                            // expand
    -> self.templates                           // expand
    -> self.scan(paths)                         // expand
    -> self.generate_output()                   // expand
    -> self.add_generate_header_to_generated()  // plain
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
    -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work
  satisfy() @agent_instructions
    -> self.mode = "tool"                       // plain
    -> self.validate()                          // expand — includes finish_turn @agent_tool
    -> self.generate_fixes_from_validate()      // expand
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
    -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work
  scan(paths) @agent_tool
    -> self.scanner.scan(paths)                 // plain
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  createRule(failed, wanted) @agent_instructions
    -> self.turn.open(self)             // plain — session already open
    -> self.contexts                            // expand
    -> self.examples                            // expand
    -> self.templates                           // expand
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
    -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work
  // drop forwards: ensure_session, create_session, close_session,
  //   read_context_index, record_context_root, begin_eval_turn, finish_eval_turn,
  //   log_mistake, log_correction, repair
  // subclasses: contexts, examples, templates, scan, generate_output, …

  ---- host.workspace (Workspace)
WorkSession
  workspace Workspace                     // back-ref — one of parent.workSessions
  path name folder goal fidelities contexts
  turns openTurn repairs
  git GitRepo
  session_branch scope_paths dirty
  open(name, goal, fidelities, contexts, path)
    -> git.checkout_or_create(session_branch)
  close(outcome, handoff) save() load()
  ----
  Workspace
    path
    workSessions list[WorkSession]
    currentWorkSession WorkSession | None
    pathOverrides list[PathOverride]
    openWorkSession(...) load() save() lookupPath() upsertPath()
  SessionPaths
  ----
  ToolCall
    toolset name summary ok error role  // role=expansion|run optional metadata
  TurnCommit
    turnId sessionName toolNames sha
    // identity = git SHA; turn metadata in commit message body + trailers
    // mistake/correction association is NOT mirrored here as a yaml list
  ----
  // Git-primary change fidelity (LOCKED)
  // Association rule: Mistake = note on introducing SHA; Correction = new session-branch
  //   commit with Fixes-Mistake trailers + payload linking entry_ids → introducing SHAs.
  //   session.yaml / events.log are NOT the association store. Merge topology deferred.
  // Mistake note payload: entry_id, artifact, rule, wrong, original, tool, fidelity (+ introducing SHA)
  // Correction commit payload: improved, how, status, entry_ids[] (+ fix SHA; each id → introducing SHA)
  //   Mistake  → git notes (optional annotated tag mistake/<id>) on introducing commit SHA
  //   Correction → new commit on session branch + trailers Fixes-Mistake: <id>… (optional notes both ways)
  //   Exact change body → git show <sha> — do not duplicate as primary store
  //   session.yaml → bootstrap only (name, branch, workspace path, HEAD); not mistake index
  //   SessionLog / events.log → in-turn expand|run audit only — not mistake/correction association
  //   mistakes/{slug}/ and repairs/ folder trees → not primary association store (Repair nest deferred)

  ---- workspace package (peer — not on WorkSession)
SessionLog                              // session_log.py — own class; binds WorkSession
  bind(session) set_session(session)
  append(toolset, name, summary, ok, error, role, payload)  // expand (framework) or run (author)
    -> events.log line: ts toolset=… name=… ok=… summary=… [error=…] [role=expansion|run] [payload=…]
    -> openTurn.toolCalls.add(ToolCall(...))  // same fields — expansion and run both land on turn
    // never the store for Mistake↔Correction↔commit links

  ---- Turn kit (host.turn) vs turn state (workspace.openTurn) — same class, one owner
Turn : AgenticToolset                   // manifest: turn.turn:Turn
  workSession WorkSession               // back-ref when attached as openTurn
  prompt result context toolCalls changeCommit
  commitMessage
  open(host)                                // plain — open turn; reuse openTurn only on failure/recovery
    if host.workspace.openTurn is None:
      host.workspace.openTurn = Turn(workSession=host.workspace)
    return host.workspace.openTurn
  finish_turn(tools, prompt, result, context) @agent_tool
    for host in context_tools(tools):
      host.workspace.openTurn.finish(prompt, result, context)
  finish(prompt, result, context)       // domain — called by finish_turn @agent_tool
    self.prompt = prompt; self.result = result; self.context = context
    changeCommit = None
    if workSession.dirty:
      sha = workSession.git.commit(workSession.scope_paths, commitMessage)
      // commitMessage may carry trailers (e.g. Fixes-Mistake) when this turn is a correction
      changeCommit = TurnCommit.from(self, sha)
      workSession.turns.add(self)
    workSession.git.push()                // always — session branch to origin
    workSession.openTurn = None
    workSession.save()                    // bootstrap yaml only — not mistake index rewrite
    return changeCommit
  record_mistake(tools, artifact, rule, wrong, original, tool, fidelity, introducing_commit) @agent_tool
    for host in context_tools(tools):
      if host.workspace.openTurn is None: host.workspace.openTurn = Turn(workSession=host.workspace)
      mistake = Mistake(..., introducingCommit=introducing_commit)
      mistake.annotate(host.workspace.git)   // notes on introducing commit — NOT on open turn commit
  record_correction(tools, entry_ids, improved, how, status) @agent_tool
    for host in context_tools(tools):
      if host.workspace.openTurn is None: host.workspace.openTurn = Turn(workSession=host.workspace)
      mistakes = host.workspace.git.find_mistakes(entry_ids)  // resolve via notes/tags on session branch
      correction = Correction(...)
      each mistake: correction.add(mistake)
      host.workspace.openTurn.pendingCorrection = correction
      // link lands when finish commits: trailers on this turn's SHA + optional notes on mistake SHAs

  ---- workspace.git
GitRepo
  root
  current_branch                        // property — read HEAD branch name
  current_commit                        // property — read HEAD sha
  branch                                // property: get -> current_branch
                                        // set -> checkout(branch) switch only; branch must exist
  create_branch(branch)               // internal — git branch; ref only, no switch
  checkout_or_create(branch)            // if missing create_branch; then branch = branch
  is_dirty(scope_paths)                 // low-level; prefer WorkSession.dirty
  commit(paths, message) sha            // message may include trailers
  push()                                // git push -u origin <current branch>; called from Turn.finish every turn
  note(sha, namespace, payload)             // git notes — annotate commit without rewriting history
  read_notes(sha, namespace)
  find_mistakes(entry_ids) Mistake      // resolve mistake notes/tags on session branch commits
  // branch setter     ≈ git switch/checkout (existing branch)
  // create_branch     ≈ git branch (create ref, stay on current HEAD)
  // checkout_or_create ≈ git switch -c when new, else git switch

  ---- workspace.repairs / turn.mistakes (eval domain — not agentic)
Mistake                                 // resource — not agentic; identity hangs off introducing commit
  entry_id artifact rule wrong original tool fidelity
  introducingCommit sha                 // commit that made the faulty change (session branch)
  correction Correction                 // 0..1 — set by Correction.add(mistake)
  annotate(git)                         // git.note(introducingCommit, payload) — payload MUST include:
    //   entry_id, artifact, rule, wrong, original, tool, fidelity, introducingCommit
    // optional tag mistake/<entry_id> → introducingCommit
  // exact tree/diff fidelity = git show introducingCommit — original is curated excerpt for agents, not a second full-file store

Correction                              // resource — not agentic; identity hangs off fix commit
  improved how status
  mistakes Mistake                      // collection — mistakes this correction fixes
  fixCommit sha | None                  // set when correction turn finishes (this turn's commit)
  add(mistake)                          // mistakes.add; mistake.correction = self
  link(git)                             // on fixCommit — trailers + note payload MUST include:
    //   improved, how, status, mistake entry_ids[], fixCommit
    //   Fixes-Mistake: <entry_id>… trailers; each entry_id resolves to that mistake's introducingCommit
  // association lives on the branch graph — one place — not session.yaml + trail + folder tree

Repair                                  // resource — themed improvement bucket on WorkSession (deferred nest)
  theme status backlog | finished
  mistakes Mistake
  correction Correction
  bddEvals
  improvement_md                          // {folder}/repairs/{theme}/improvement.md
  tools_git GitRepo                       // optional CDD clone root — composed at caller, not subclass
  open(host, asset, violation)            // ensure mistakes on turn; copy to tools_git session if needed
  verify_fix()                            // regression artifacts -> bddEvals
  nest(mistakes)                          // same-theme mistakes under repairs/{theme}/ — deferred from usage story
  finish(turn)                            // status = finished

  ---- who calls GitRepo (CE must show composition from owner; callers use owner's git)
  // WorkSession.git  — session branch at workspace root
  //   WorkSession.open        -> git.checkout_or_create(session_branch)
  //   WorkSession.dirty       -> git.is_dirty(scope_paths)
  //   Turn.finish             -> workSession.git.commit(...); workSession.git.push()
  // Repair.tools_git — optional second repo at CDD/tools clone root (0..1)
  //   Repair.open             -> tools_git checkout/commit when repair spans clone

  ---- peer kit (invoked via slash / manifest — not composed on BaseContextTool)
Improvement : AgenticToolset
  repair(tools, asset, violation) @agent_instructions
    for host in tools:
      -> repair = host.workspace.repairs.for_violation(asset, violation)
      -> repair.open(host, asset, violation)
  verify_fix(tools, theme) @agent_tool
    for host in tools:
      -> host.workspace.repairs[theme].verify_fix()
```

**Relationships (target CE)**

Draw **associations** (who calls whom) and **composition** (who owns whom).

| CE edge | Meaning |
|---|---|
| `BaseContextTool` ◆— `Workspace` | Paths/overrides direct — **`lookupPath`**, **`path`**, **`pathOverrides`** |
| `Workspace.currentWorkSession` → `WorkSession` | Current work session — turn, git, repairs |
| `Workspace` ◆— `WorkSession` via `workSessions` | All work sessions under `.context/sessions/` |
| `Workspace.pathOverrides` | `{tool, fidelity, path}` rows — file `{workspace.path}/.context/context-index.md` |
| `WorkSession` ◆— `Turn` via `openTurn` | Turn **state** — prompt, toolCalls, mistakes, commit |
| `WorkSession` ◆— `GitRepo` via `git` | Git at `find_git_root(workspace.path)` — not necessarily `workspace.path` |
| `Turn` → `GitRepo` via `workSession.git` | **Association** — `finish` calls `commit` / `push` (dashed arrow; not composition) |
| `WorkSession` → `SessionPaths` | Work-session path helpers (`docs_dir`) |
| `SessionLog` → binds `WorkSession` | Audit trail under `{folder}/logs/` |
| `Turn` ◆— `ToolCall`, `Mistake`; `Turn` → `TurnCommit` | Turn contents |
| `Mistake` → `Correction`, domain `Repair` | Eval domain chain |
| `Repair` ◆— `GitRepo` via `tools_git` (0..1) | Optional CDD/tools-clone repo for repair work |
| **No** `BaseContextTool` → `Turn` | Host does not own turn state |

**Who calls `GitRepo` (and how CE shows it)**

| Caller | Access path | CE edge | Calls |
|---|---|---|---|
| **WorkSession** | `git` | **`WorkSession` ◆— `GitRepo`** (composition) | `open` → `checkout_or_create(session_branch)`; `dirty` → `is_dirty(scope_paths)` |
| **Turn** | `workSession.git` | **`Turn` → `GitRepo`** (association, dashed) | `finish` → `workSession.git.commit(scope_paths, …)` then `workSession.git.push()` |
| **Repair** | `tools_git` | **`Repair` ◆— `GitRepo`** (composition, optional) | `open` → clone checkout/commit when repair spans the tools root |

Turn does not **own** a `GitRepo` — it **uses** the session's via `workSession.git`. Draw both: composition **`WorkSession` ◆— `GitRepo`**, and association **`Turn` → `GitRepo`** labeled `workSession.git`.

**`host.turn` vs `currentWorkSession.openTurn`:** **`Turn.open(host)`** reads/writes **`host.workspace.currentWorkSession.openTurn`**. Do not draw **BaseContextTool → Turn** as structural ownership alongside **WorkSession → Turn**.

---

## 5. Future agent surface

**No compat shims.** Delete removed APIs — do not re-export under old names on host or kit.

**Gone from host:** `log_mistake`, `log_correction`, `begin_eval_turn`, `finish_eval_turn`, `repair`, `self.repairer`, `host.eval`, `_bind_eval`, `Session` / `WorkspaceSession` / `EvalSession` types and imports, eval `Repair` toolset.

**Two agentic kits** for turn/eval (session prelude is plain on **WorkSession**, **run** from **BaseContextTool.generate** / **validate**):

| Kit | `@agent_tool` (agent sees) | Plain (host runs in prelude) |
|---|---|---|
| **Turn** | `finish_turn`, `record_mistake`, `record_correction` | `open(host)` — plain; opens turn (prelude only) |
| **Improvement** | `verify_fix` | — |
| | `repair` is `@agent_instructions` | |

**WorkSession** — plain `open` / `close` on `host.workspace`; **`open`** loads index and **`upsert(tool, fidelity, path)`** only when ≠ default.

### How the agent uses Turn (never touches `openTurn` directly)

`openTurn` is **internal state** on `host.workspace` — not a host `@tool`, not a host `@resource`, not on the Bdd manifest.

The agent invokes **`self.turn.finish_turn(tools, prompt, result, context)`**, **`Turn.record_mistake(...)`**, **`Turn.record_correction(...)`** — each **`@agent_tool`** on **Turn**.

Interaction (CE sketch notation; `->` = real call; `// plain | expand | @agent_tool`):

```
# /generate — host @agent_instructions (not a separate lifecycle kit)

Agent
  /generate skill
    -> Bdd.generate                              // expand host action directly

BaseContextTool (Bdd)
  generate @agent_instructions
    -> self.workspace.open()                   // plain
    -> self.turn.open(self)             // plain
    -> self.decisions.record_decisions_session()
    -> self.contexts                            // expand
    -> self.examples                            // expand
    -> self.templates                           // expand
    -> self.generate_output()                   // expand
    -> self.add_generate_header_to_generated()
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
    -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work

----
WorkSession
  open()                                         // plain — this host's session
    -> checkout branch, index, record root

Turn
  open(host)                                   // plain — open turn for this run
    if host.workspace.openTurn is None:
      host.workspace.openTurn = Turn(workSession=ws)
    // else: failure/recovery — openTurn still set; reuse
  finish_turn tools … @agent_tool
    -> openTurn.finish prompt result context

# /record_mistake — direct Turn kit @agent_tool

Agent
  -> Turn.record_mistake tools …

Turn
  record_mistake … @agent_tool
    -> openTurn.record_mistake mistake
    // openTurn on host.workspace; not agent-visible
```

**Three exposure paths:**

| Path | Agent invokes? | Lands on turn via |
|---|---|---|
| Turn prelude | no — **run** in `BaseContextTool.generate` | `self.turn.open(self)` — open turn for this run |
| Turn close | yes — **`self.turn.finish_turn(tools, prompt, result, context)`** `@agent_tool` | `openTurn.finish(...)` |
| Instruction **expand** | no — framework on `@agent_instructions` expand | `SessionLog.append` → **events.log** + **openTurn.toolCalls** (`role=expansion`) |
| Action **run** audit | no — explicit `SessionLog.append` at end of recipe | same record → **events.log** + **openTurn.toolCalls** (`role=run`) |
| Mistake / correction | yes — `record_mistake` / `record_correction` **@agent_tool** | **git notes** on introducing SHA (entry_id, artifact, rule, wrong, original, tool, fidelity); **fix commit** trailers + payload (improved, how, status, mistake entry_ids) |

Auditable `@agent_instructions`: framework logs **expand**; author logs **run** at end of body — both via `SessionLog.append`, not `@agent_tool`.

**Host (Bdd, Cdd, …)** keeps only domain work: `generate`, `validate`, `document`, `satisfy`, `contexts`, `examples`, `scan`, … Host **does not** re-export session or eval tools.

### Manifest shape (example Bdd)

```yaml
# host toolset — Bdd
actions:
  generate: { tools: [] }      # expansion names kits below, not host forwards
  validate: { tools: [] }
  repair:   { tools: [] }      # -> Improvement.repair(tools, …)

# turn kit — turn.turn:Turn
Turn:
  finish_turn: { kind: tool, parameters: { tools, prompt, result, context } }
  record_mistake: { kind: tool, parameters: { tools, artifact, rule, wrong, original, tool, fidelity } }
  record_correction: { kind: tool, parameters: { tools, entry_id, improved, how, status } }
  // open — plain; not on manifest

Improvement:
  repair: { kind: action, parameters: { tools, asset, violation } }
  verify_fix: { kind: tool, parameters: { tools, theme } }
```

### When things run

```
Prerequisite: host run — self.workspace.open() + self.turn.open(self) (plain)

/generate @agent_instructions (Bdd.generate):
  -> self.workspace.open(); self.turn.open(self)  // plain — open turn
  -> … domain steps …
  -> SessionLog.append(...)  // plain — run
  -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work

/validate — same: prelude, domain, SessionLog, self.turn.finish_turn in recipe
```

### Call chain (mistake)

```
Agent
  -> Turn.record_mistake(tools, artifact, rule, wrong, original, tool, fidelity, introducing_commit)  @agent_tool
    for host in tools:
      -> mistake = Mistake(..., introducingCommit=introducing_commit)
      -> mistake.annotate(host.workspace.git)
           // git.note on introducing commit — not on open turn's commit
    <- entry_id
```

### Call chain (correction)

```
Agent
  -> Turn.record_correction(tools, entry_ids, improved, how, status)  @agent_tool
    for host in tools:
      -> mistakes = host.workspace.git.find_mistakes(entry_ids)
      -> correction = Correction(...)
      -> each mistake: correction.add(mistake)
      -> openTurn.pendingCorrection = correction
  // later — turn finish commits the fix; trailers Fixes-Mistake on that SHA; correction.link(git)
```

### Logging

**`SessionLog.append(...)`** — own workspace package class. **Expand:** framework on `@agent_instructions` expand. **Run:** explicit call at end of auditable recipe bodies. Not `@agent_tool`. Delete `@log` decorator and runner run hooks (see §4). **Not** the store for mistake↔correction↔commit association — that is git notes + commit trailers.

Turn **@agent_tool**s and `openTurn` domain methods share names on the **same class**. **Mistake** / **Correction** are not agentic.

### Gate

All Turn / Improvement ops require **WorkSession open** (`host.workspace.name` set). No `eval is None` check — turns live on `workspace` directly.

---

## 6. Agent surface — summary table

**Four ways data lands on `openTurn`:**

| Mechanism | Agent invokes? | Lands on turn via |
|---|---|---|
| Turn envelope | yes — `finish_turn` **@agent_tool** in orchestrator instructions | `openTurn.finish(...)` |
| Instruction **expand** | no — framework on `@agent_instructions` expand | `SessionLog.append` → **events.log** + **openTurn.toolCalls** (`role=expansion`) |
| Action **run** audit | no — explicit `SessionLog.append` at end of recipe | same record → **events.log** + **openTurn.toolCalls** (`role=run`) |
| Mistake / correction | yes — `Turn.record_mistake` / `Turn.record_correction` **@agent_tool** | **git notes** on introducing SHA; **trailers** on fix commit — not openTurn.mistakes list / yaml index |

**One Turn class** — **@agent_tool** fans out; domain methods on `openTurn`.

Auditable `@agent_instructions`: framework logs **expand**; author logs **run** at end of body.

**Typical `/generate` flow (open → work → close):**

```
Bdd.generate() @agent_instructions
  -> self.workspace.open()                   // plain
  -> self.turn.open(self)             // plain
  -> self.decisions.record_decisions_session()
  -> self.contexts, self.examples, self.templates, self.generate_output()
  -> self.add_generate_header_to_generated()
  -> SessionLog.append(...)                  // plain — run
  -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work

Bdd.validate() @agent_instructions
  -> self.workspace.open(); self.turn.open(self)
  -> self.contexts; self.scan()
  -> SessionLog.append(...)
  -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work
```

---

## 7. Cross-module interaction (target)

```
Bdd.generate() @agent_instructions
  -> self.workspace.open(); self.turn.open(self)
  -> … domain steps …
  -> SessionLog.append(...)
  -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work

Turn.finish_turn(tools, prompt, result, context) @agent_tool
  -> openTurn.finish(...)

Bdd.validate() @agent_instructions
  -> self.workspace.open(); self.turn.open(self)
  -> self.contexts; self.scan()
  -> SessionLog.append(...)
  -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work

Turn.finish_turn(tools, prompt, result, context) @agent_tool
  -> openTurn.finish(...)

Turn.record_mistake(tools, ..., introducing_commit) @agent_tool
  -> Mistake(...).annotate(git)   // notes payload on introducing commit

Turn.record_correction(tools, entry_ids, ...) @agent_tool
  -> Correction(...); each mistake: correction.add(mistake)
  // finish: fix commit + correction.link(git) — improved, how, status, entry_ids

Improvement.repair(tools, asset, violation) @agent_instructions
  for host in tools:
    -> repair = host.workspace.repairs.for_violation(asset, violation)
    -> repair.open(host, asset, violation)

Improvement.verify_fix(tools, theme) @agent_tool
  -> repairs[theme].verify_fix() -> bddEvals on Repair
```

**Seam rules**

- **GitRepo** — git-shaped surface: `branch` setter switches to an **existing** ref; `create_branch` creates ref only (internal); `checkout_or_create` creates if missing then sets `branch`; **`note` / `read_notes` / `find_mistakes`** for mistake annotation without rewriting history. **Composed on `WorkSession.git`** (session repo) and optionally on **`Repair.tools_git`** (tools clone). **`Turn.finish`** commits and pushes via **`workSession.git`** — draw **`Turn` → `GitRepo`** association (not composition).
- **WorkSession** — `session_branch`, `scope_paths`, `dirty` as properties; holds `git` (**GitRepo** — sole session-repo owner), `openTurn` (**Turn** instance — sole turn-state owner), turn index, repairs backlog. **`open`** checks out session branch; **`dirty`** delegates to `git.is_dirty`. **`save`/`session.yaml`** bootstrap only — not mistake index.
- **Turn** — one class: agentic kit *and* `WorkSession.openTurn`. **`host.turn`** is the composed kit for prelude + manifest; **`openTurn`** is runtime state. **`open(host)` plain** — open turn for this run; **`finish_turn` / `record_mistake` / `record_correction` `@agent_tool`**. Logging is **`SessionLog`** (workspace package), plain run — not on Turn kit. CE: **`WorkSession` → `Turn` only** — no host → Turn edge.
- **Mistake** / **Correction** — Git-primary: mistake **annotates introducing commit**; correction **links fix commit → mistake commits** (trailers + optional notes). `Correction.add(mistake)` wires in-memory; **no** primary persist to `mistakes/` / yaml turn rows.
- **Repair** (domain) — themed bucket with `open`, `verify_fix`, `nest`, `finish`; holds optional `tools_git GitRepo`. Nest deferred from usage story.
- **Improvement** — thin `/repair` orchestrator over domain Repair resources; no runner/loop type.
- No EvalSession / `host.eval`.

---

## 8. Slash alignment (target)

```
generate | validate | satisfy | document
  -> Bdd.generate | Bdd.validate | … @agent_instructions on BaseContextTool
     -> workspace.open + turn.open  // plain
     -> domain body                         // expand
     -> self.turn.finish_turn(tools, prompt, result, context)  // @agent_tool on Turn; agent invokes after work
  // delete HostLifecycle kit; revert agent_skills kit-owned routing for generate/validate/…

repair
  -> Improvement.repair(tools, asset, violation) @agent_instructions

record_mistake
  -> Turn.record_mistake(tools, …) @agent_tool

record_correction
  -> Turn.record_correction(tools, …) @agent_tool

turn
  -> self.turn.finish_turn(tools, prompt, result, context) @agent_tool
    -> openTurn.finish(...)
```

---

## 9. Refactor slices (order)

1. **Annotations** — **`@agent_instructions` / `@agent_tool` only**; delete `@action`, `@tool`, `@log`, `@plain_operation` (no aliases); explicit **`SessionLog.append(...)`** in auditable recipe bodies.
2. **Naming** — **`WorkSession` only**; **`host.workspace`** → **`Workspace`** (code today holds WorkSession); **`workspace.currentWorkSession`** for the current work session; delete `Session`, `WorkspaceSession`, `EvalSession`.
3. **Session prelude** — `WorkSession.open` plain (load index; upsert when path ≠ default); **`Turn.open` plain**; **`finish_turn` `@agent_tool`**.
4. **GitRepo seam** — rename `WorkspaceRepo` → `GitRepo`; drop `ensure_session_branch` / `commit_on_session_branch` / `CDDRepo extends`.
5. **Turn on WorkSession** — `openTurn` is a **Turn** instance; commit in `Turn.finish`.
6. **Resources** — domain `record_*` on openTurn; Mistake/Correction `persist`; domain **Repair** with `open` / `verify_fix` / `nest` / `finish`.
7. **BaseContextTool lifecycle** — prelude **plain run** + domain steps + **`self.turn.finish_turn(tools, prompt, result, context)`** in `generate` / `validate` recipe; **delete HostLifecycle** kit and kit-owned routing for lifecycle actions.
8. **Bind at open** — `WorkSession.open()` on each host; delete `_bind_eval` / `host.eval`.
9. **Turn** + **Improvement** — delete host eval forwards and eval `Repair` toolset.
10. **Host slim** — domain `@agent_instructions` only; no session/turn/repair re-exports.
11. **Specs** — agent BDD: generate prelude summary replaces `ensure_session` / `read_context_index` in expansion **tools** list.

### Workspace module checklist

1. **`Workspace`** — `path`; `workSessions`; **`currentWorkSession`**; `pathOverrides`; `load` / `save` / `lookupPath` / `upsertPath` / **`openWorkSession`**.
2. **`PathOverride`** — `tool`, `fidelity`, `path`; file `context-index.md` is persistence only.
3. **`WorkSession`** — back-ref `workspace`; owns `openTurn`, `turns`, `repairs`, `git`.
4. **`BaseContextTool.workspace`** → **`Workspace`** (code today holds WorkSession). Paths direct; turn/git via **`currentWorkSession`**.
5. **`openWorkSession`** — load overrides; upsertPath when ≠ default; set **`currentWorkSession`**.
6. Rename `WorkspaceRepo` → `GitRepo`; `branch` property (set = switch); internal `create_branch`; `checkout_or_create`; **`push()`**.
7. Move branch policy to `WorkSession.session_branch` property; dirty via `WorkSession.dirty`.
8. `Turn.finish` uses `commitMessage`; calls `workSession.git.commit(scope_paths, message)` when dirty; **always** `workSession.git.push()` before clearing `openTurn`.
9. **SessionLog** — keep as own workspace class; delete `@log` / runner run-branch / **`control`**; **`append` → events.log + openTurn.toolCalls** for **expand** (framework) and **run** (explicit); add **`role`** metadata; extend **ToolCall** with `ok`, `error`, `role`.
10. Update `module-context.md` — **`Workspace` ◆— `WorkSession`** (many). *(CE diagram: user-owned.)*

### Eval module checklist

1. Delete `EvalSession` turn ownership — move Turn/TurnCommit to WorkSession.
2. **Mistake**, **Correction**, **Repair** (domain resources) stay in eval package; **Git-primary** association (notes + trailers on session branch). `session.yaml` bootstrap only — not mistake index. Repair nest deferred.
3. Delete `CDDRepo` subclass — domain **Repair.tools_git** composes `GitRepo(tools_root)`.
4. Split eval `Repair` toolset → **Turn** (turn **@agent_tool**s) + **Improvement**.
5. `verify_fix` attaches BDD eval artifacts to domain Repair.
6. Update `eval-ce.drawio` + `module-context.md`.

---

## 10. Open questions

- Path scope for `GitRepo.commit` — whole repo root vs `{path}` only?
- When does Repair move backlog → finished?

---

## 11. Out of scope

- Relocating `utilities/eval` → `context_tools/actions/eval`.
