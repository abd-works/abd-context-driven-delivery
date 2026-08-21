# Sketch — workspace ↔ eval OO realignment

Session **eval-consolidate-workspace**. CE sources: `context_tools/actions/workspace/.context/workspace-ce.drawio`, `context_tools/actions/eval/.context/eval-ce.drawio`.

---

## 1. Problem

Workspace and eval both use **Session** vocabulary, compose each other through **BaseContextTool** (`_bind_eval`, `repairer`), and split git/logging seams inconsistently — while slash commands invert other kits (`/repair`, `/partition`, …) to **kit owns run, tools are arguments**. The CE diagrams encode extra types (`WorkspaceSession` stub, `Repair` twice) that do not match code.

**Vocabulary (target):** a **work session** holds **turns** (prompt, tools, commit). **Turns** hold **mistakes**. **Mistakes** group by theme into **repairs** — backlog or finished. **`GitRepo`** is a thin git facade (no domain vocabulary). **Prefer properties for derived/read state**; operations only for mutations and agent-facing tools.

---

## 2. Current model — workspace

From `workspace-ce.drawio` + `workspace_session.py`:

```
WorkSession (implicit — host composes Session)
  Session                    ← alias: WorkspaceSession
    path, name, goal, …
    open / ensure_session / create_session / close_session
    read_context_index / record_context_root
    ----
  SessionPaths
    docs_dir(destination)
  ContextIndex
    lookup_root / upsert_entry / …
  GitRepo
    root current_branch current_commit    // read — properties
    branch                                // property: get=HEAD branch; set=switch to existing
    create_branch checkout_or_create commit
    // create_branch internal; branch= switches only; checkout_or_create=create ref + switch
  NullGitRepo
  SessionLog                 ← binds Session; append runner audit events (today: @log-marked only)
  GitConnectError / DirtyBranchSwitchError
```

**Relationships**

- `SessionLog` → binds `Session`, appends under `{folder}/logs/`
- `Session` → uses `ContextIndex`; git via ephemeral `GitRepo` with domain method names (`ensure_session_branch` ⚠)
- `BaseContextTool.workspace` → composed `Session` instance
- Eval imports `WorkspaceSession` (= `Session`) as **location** for `EvalSession` (to be removed — turns live on WorkSession)

### Workspace leaks

| Issue | Symptom |
|---|---|
| **Name: Session** | Same word as eval domain (`EvalSession`, and `Session = EvalSession` in eval). Cannot tell work-session folder from eval document. |
| **Session does too much** | Lifecycle tools + path/index state + implied git. CE lists git ops on `Session` that belong on `GitRepo` + WorkSession policy. |
| **GitRepo domain leak** | `ensure_session_branch` / `commit_on_session_branch` encode work-session branch naming — belongs on WorkSession. |
| **Git on wrong aggregate** | `commit_on_session_branch` called from **EvalSession.finish_turn**; checkout vs commit not split cleanly. |

---

## 3. Current model — eval

From `eval-ce.drawio` + `eval/session.py` — **target removes EvalSession as turn owner**.

```
EvalSession (to remove)            ← alias: Session = EvalSession ⚠
  workspace: WorkspaceSession
  turns, openTurn, mistakes      ← turns should move to WorkSession
  repairs: list[Repair]          ← domain runs ⚠ same name as toolset
  begin_turn / finish_turn         ← move to Turn (WorkSession.openTurn)
  ----
  Turn, ToolCall, TurnCommit, Mistake, Correction
  Repair : AgenticToolset          ← bundles record + run ⚠ split → Turn + Improvement
  Archive
```

**Relationships (diagram)**

- `EvalSession` ◆— `WorkspaceSession` (location)
- `EvalSession` → `GitRepo` via domain wrappers (`commit_on_session_branch` ⚠)
- `EvalSession` ◆— `Repair` toolset instances in `_repairs`
- `Repair` → `cddSession`, `Scan`, `BaseContextTool`
- `Turn` ◆— `ToolCall`; `Turn` → `TurnCommit`
- `Mistake` ◆— `Correction` → fixedIn `Turn`

### Eval leaks

| Issue | Symptom |
|---|---|
| **`Session = EvalSession`** | Import trap — work session vs eval session document. |
| **EvalSession owns turns** | Turn lifecycle belongs on **Turn** (`WorkSession.openTurn`); eval package owns mistake/repair domain only. |
| **Two “Repair” types** | Toolset bundles record + run; same name as themed repair bucket — split toolsets and domain **Repair**. |
| **`Repair.eval()` action** | Overloads package/session vocabulary. |
| **Eval on host init** | `_bind_eval()` + `repairer` at construction, not at `open`. |
| **`host.eval` vs `workspace.eval`** | Split attribute; SessionLog uses workspace side. |
| **CDDRepo extends GitRepo** | Eval/repair behavior on repo type — use second `GitRepo(tools_root)` at caller. |
| **Nested EvalSession** | `cdd_session` on CDD clone — no primary vs clone stereotype in CE. |
| **No turn toolset** | `begin_eval_turn` / `finish_eval_turn` on host; target: **Turn** kit owns turn **@agent_tool**s. |
| **WorkspaceSession stub** | CE shows `{ path, folder, open }` — `open` is not a field. |

---

## 4. Target model — aggregate boundaries

Domain chain: **WorkSession → Turn → Mistake → Repair (themed, backlog | finished)**.

**Resource-oriented split:** **Turn** is one class — agentic kit *and* `WorkSession.openTurn`. **Mistake** / **Correction** persist files only (`persist`). **Improvement** owns `/repair`.

### Agent annotations & invoke semantics (target — changes from today)

**Only two author annotations:** `@agent_instructions`, `@agent_tool`. Everything else is plain Python or framework behavior — not a decorator authors apply.

| Today (remove as author markers) | Target |
|---|---|
| `@action` | `@agent_instructions` (rename only during migration) |
| `@tool` | `@agent_tool` (rename only during migration) |
| `@log` | **drop** — explicit plain `SessionLog.append(...)` in the method body |
| `@plain_operation` | **drop** — unmarked methods are plain; no decorator |

Legacy aliases during migration: `@action` → `@agent_instructions`, `@tool` → `@agent_tool`. Do **not** add new `@log` usage.

When an **`@agent_instructions`** recipe is invoked, the framework walks the body. **What happens depends on the callee annotation — not on which class owns the recipe.**

| Callee | Behavior | Agent sees |
|---|---|---|
| Plain method (no annotation) | **run** — execute as Python now; summary in prelude / response | Not on tool list |
| `@agent_tool` | **expose** — list in expansion `tools`; agent invokes later (body runs on invoke) | Tool name + when-to-use from recipe prose |
| `@agent_instructions` | **expand** — inline nested recipe (callee `mode="tool"` → defer like a tool step) | Inlined instructions |

**Logging — only change from today:** Drop `@log` decorator and invoke-runner log branching. **`SessionLog` stays its own class** in `context_tools/actions/workspace/session_log.py` — do not fold into `WorkSession`, do not move to the host.

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
- **Drop invalid kinds from today:** no **`control`**. Retire `apply_log_control` / `log_full` control lines. Retire `@log` / `is_logged` / runner run-branch logging — replaced by explicit run append + framework expand append.
- **`tool` / `action` / `expansion` on `events.log`:** retire as **filters**; optional **`role`** metadata only.

Run append: after prelude, before `return`. Expand append: in action expand path (today `_log_expansion` → unified `SessionLog.append`).

### Fix logging (sketch note — not in this refactor pass)

Remove `@log`, `is_logged`, `member_is_logged`, runner run-branch logging, **`control`** lines. **Keep `SessionLog` as its own class.** **`append` → events.log + openTurn.toolCalls** for both **expand** (framework) and **run** (explicit in recipe).

**Decisions (locked):**

- Any `@agent_instructions` body may **run** plain code — hosts and kits alike.
- Plain code is just code — any callable in the body may run; no receiver whitelist.
- **`finish_turn`** stays **`@agent_tool`** — listed in orchestrator instructions; agent supplies prompt/result/context.
- **Session prelude** (`open`, begin turn) — **plain only**; no `@agent_tool`. Resume-or-create, index, record root, branch checkout live inside `open` / `ensure_open`; return validation text when name/path missing. Drop `ensure_session` / `create_session` / `read_context_index` / `record_context_root` as agent tools (no standalone slash; agent BDD specs that assert them in generate **tools** list update to prelude summary).

**Generate envelope — on `BaseContextTool` (Bdd, Cdd, …), not a separate orchestrator class:**

```
BaseContextTool.generate @agent_instructions   // /generate → Bdd.generate directly
  -> self.workspace.open()                   // plain
  -> self.turn.ensure_open(self)             // plain
  -> self.decisions.record_decisions_session()  // plain
  -> self.contexts                            // expand
  -> self.examples                            // expand
  -> self.templates                           // expand
  -> self.generate_output()                   // expand
  -> self.add_generate_header_to_generated()  // plain
  -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  // expose finish_turn @agent_tool — agent invokes after work; not inline here
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

Host **`generate` / `validate`** drop eval forwards; prelude **run** + domain **expand** + `finish_turn` **expose** live in the host `@agent_instructions` body.

**Read top-down:** **`BaseContextTool`** is the entry point (Bdd, Cdd, …). You start with the host; **`workspace`**, **`turn`**, git, and eval resources are composed **from** it — not parallel roots.

```
BaseContextTool : AgenticToolset          // START HERE — Bdd, Cdd, Stories, … the host
  workspace WorkSession                   // composed session state for this tool
  turn Turn                               // companion kit — finish/record @agent_tool; ensure_open plain
  generate() @agent_instructions
    -> self.workspace.open()                   // plain
    -> self.turn.ensure_open(self)             // plain
    -> self.decisions.record_decisions_session()  // plain
    -> self.contexts                            // expand
    -> self.examples                            // expand
    -> self.templates                           // expand
    -> self.generate_output()                   // expand
    -> self.add_generate_header_to_generated()  // plain
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  validate() @agent_instructions
    -> self.workspace.open()                   // plain
    -> self.turn.ensure_open(self)             // plain
    -> self.contexts                            // expand
    -> self.scan()                              // expand
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  document(paths) @agent_instructions
    -> self.workspace.open()                   // plain
    -> self.turn.ensure_open(self)             // plain
    -> self.contexts                            // expand
    -> self.templates                           // expand
    -> self.scan(paths)                         // expand
    -> self.generate_output()                   // expand
    -> self.add_generate_header_to_generated()  // plain
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  satisfy() @agent_instructions
    -> self.mode = "tool"                       // plain
    -> self.validate()                          // expand
    -> self.generate_fixes_from_validate()      // expand
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  scan(paths) @agent_tool
    -> self.scanner.scan(paths)                 // plain
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  createRule(failed, wanted) @agent_instructions
    -> self.turn.ensure_open(self)             // plain — session already open
    -> self.contexts                            // expand
    -> self.examples                            // expand
    -> self.templates                           // expand
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  // drop forwards: ensure_session, create_session, close_session,
  //   read_context_index, record_context_root, begin_eval_turn, finish_eval_turn,
  //   log_mistake, log_correction, repair
  // subclasses: contexts, examples, templates, scan, generate_output, …

  ---- host.workspace
WorkSession
  path name folder goal fidelities contexts
  session_md context_index
  turns openTurn repairs
  git GitRepo
  session_branch                        // property: f"session/{name}"
  scope_paths                           // property: path-limited dirty + commit scope
  dirty                                 // property -> git.is_dirty(scope_paths)
  open(name, goal, fidelities, contexts, path)
    // plain — on this host's workspace; resume or create
    -> git.checkout_or_create(session_branch)
    -> read_context_index()
    -> record_context_root()                  // defaults root=host.path
    // missing name/path -> return validation message (not @agent_tool)
  ensure_open_turn()                        // plain — openTurn = Turn(workSession=self) if None
  close(outcome, handoff)                     // plain — Handoff kit; not on host manifest
  save() load()
  ----
  ContextIndex
  SessionPaths
  ----
  ToolCall
    toolset name summary ok error role  // role=expansion|run optional metadata
  TurnCommit
    turnId sessionName toolNames mistakeIds sha
    // mistakeIds = mistakes on turn at finish; corrections traced via mistake.correction.fixedIn

  ---- workspace package (peer — not on WorkSession)
SessionLog                              // session_log.py — own class; binds WorkSession
  bind(session) set_session(session)
  append(toolset, name, summary, ok, error, role, payload)  // expand (framework) or run (author)
    -> events.log line: ts toolset=… name=… ok=… summary=… [error=…] [role=expansion|run] [payload=…]
    -> openTurn.toolCalls.add(ToolCall(...))  // same fields — expansion and run both land on turn

  ---- host.turn ; workspace.openTurn (same Turn class)
Turn : AgenticToolset                   // manifest: turn.turn:Turn
  workSession WorkSession               // back-ref when attached as openTurn
  prompt result context toolCalls changeCommit
  commitMessage
  mistakes Mistake
  ensure_open(host)                         // plain — prelude from BaseContextTool.generate
    if host.workspace.openTurn is None:
      host.workspace.openTurn = Turn(workSession=host.workspace)
  finish_turn(tools, prompt, result, context) @agent_tool
    for host in context_tools(tools):
      host.workspace.openTurn.finish(prompt, result, context)
  finish(prompt, result, context)       // domain — called by finish_turn @agent_tool
    self.prompt = prompt; self.result = result; self.context = context
    if not workSession.dirty:
      workSession.openTurn = None
      return None
    sha = workSession.git.commit(workSession.scope_paths, commitMessage)
    changeCommit = TurnCommit.from(self, sha)
    workSession.turns.add(self)
    workSession.openTurn = None
    workSession.save()
  record_mistake(tools, artifact, rule, wrong, original, tool, fidelity) @agent_tool
    for host in context_tools(tools):
      if host.workspace.openTurn is None: host.workspace.openTurn = Turn(workSession=host.workspace)
      mistake = Mistake(...)
      host.workspace.openTurn.record_mistake(mistake)
      mistake.persist(host.workspace)
      host.workspace.repairs.find_or_create(mistake.theme, status=backlog).nest([mistake])
  record_mistake(mistake)               // domain
    -> mistakes.add(mistake)
  record_correction(tools, entry_id, improved, how, status) @agent_tool
    for host in context_tools(tools):
      if host.workspace.openTurn is None: host.workspace.openTurn = Turn(workSession=host.workspace)
      mistakes = host.workspace.find_mistake(entry_id)
      correction = Correction(...)
      host.workspace.openTurn.record_correction(mistakes, correction)
      correction.persist(host.workspace)
      Repair.nest(mistakes)
  record_correction(mistakes, correction)   // domain
    -> correction.fixedIn = self
    -> each mistake: correction.add(mistake)

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
  commit(paths, message) sha
  // branch setter     ≈ git switch/checkout (existing branch)
  // create_branch     ≈ git branch (create ref, stay on current HEAD)
  // checkout_or_create ≈ git switch -c when new, else git switch

  ---- workspace.repairs / turn.mistakes (eval domain — not agentic)
Mistake                                 // resource — not agentic
  entry_id artifact rule wrong original tool fidelity theme folder
  repair Repair                           // 0..1 themed repair bucket
  correction Correction                   // 0..1 — set by Correction.add(mistake)
  persist(workSession)                    // write mistakes/{slug}/
  write_files()

Correction                              // resource — not agentic
  improved how status fixedIn Turn
  mistakes Mistake                        // collection
  add(mistake)                              // mistakes.add; mistake.correction = self
  persist(workSession)                    // write repairedAsset + improvement.md — after add

Repair                                  // resource — themed improvement bucket on WorkSession
  theme status backlog | finished
  mistakes Mistake
  correction Correction
  bddEvals
  improvement_md                          // {folder}/repairs/{theme}/improvement.md
  tools_git GitRepo                       // optional CDD clone root — composed at caller, not subclass
  open(host, asset, violation)            // ensure mistakes on turn; copy to tools_git session if needed
  verify_fix()                            // regression artifacts -> bddEvals
  nest(mistakes)                          // same-theme mistakes under repairs/{theme}/
  finish(turn)                            // status = finished

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

---

## 5. Future agent surface (clean — no compat shims)

**Gone from host:** `log_mistake`, `log_correction`, `begin_eval_turn`, `finish_eval_turn`, `repair`, `self.repairer`, `host.eval`, `_bind_eval`, `WorkspaceSession` alias, eval `Repair` toolset.

**Two agentic kits** for turn/eval (session prelude is plain on **WorkSession**, **run** from **BaseContextTool.generate** / **validate**):

| Kit | `@agent_tool` (agent sees) | Plain (host runs in prelude) |
|---|---|---|
| **Turn** | `finish_turn`, `record_mistake`, `record_correction` | `ensure_open(host)` — prelude only |
| **Improvement** | `verify_fix` | — |
| | `repair` is `@agent_instructions` | |

**WorkSession** — plain `open` / `close` on `host.workspace`; **BaseContextTool.generate** calls `self.workspace.open()`; not on Bdd manifest as agent tools. No `@agent_tool` for `ensure_session`, `create_session`, `read_context_index`, `record_context_root` (folded into `open`).

### How Turn is exposed (agent never touches `openTurn` directly)

`openTurn` is **internal state** on `host.workspace` — not a host `@tool`, not a host `@resource`, not on the Bdd manifest.

The agent reaches turn behavior through the **Turn kit manifest** (`turn.turn:Turn`) for `record_mistake` / `record_correction`, and through **host `@agent_instructions`** for `finish_turn` listed in the generate/validate expansion.

Interaction — Turn exposure (CE sketch notation; `->` = real call; `// plain | expand | expose` = invoke mode):

```
# /generate — host @agent_instructions (not a separate lifecycle kit)

Agent
  /generate skill
    -> Bdd.generate                              // expand host action directly

BaseContextTool (Bdd)
  generate @agent_instructions
    -> self.workspace.open()                   // plain
    -> self.turn.ensure_open(self)             // plain
    -> self.decisions.record_decisions_session()
    -> self.contexts                            // expand
    -> self.examples                            // expand
    -> self.templates                           // expand
    -> self.generate_output()                   // expand
    -> self.add_generate_header_to_generated()
    -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  // finish_turn @agent_tool — listed in expansion; agent invokes after agent work

----
WorkSession
  open()                                         // plain — this host's session
    -> checkout branch, index, record root

Turn
  ensure_open(host)                              // plain
    -> host.workspace.openTurn = Turn(workSession=ws)
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
| Turn prelude | no — **run** in `BaseContextTool.generate` | `openTurn = Turn(workSession=ws)` |
| Turn envelope close | yes — `finish_turn` **@agent_tool** in instructions | `openTurn.finish(...)` |
| Instruction **expand** | no — framework on `@agent_instructions` expand | `SessionLog.append` → **events.log** + **openTurn.toolCalls** (`role=expansion`) |
| Action **run** audit | no — explicit `SessionLog.append` at end of recipe | same record → **events.log** + **openTurn.toolCalls** (`role=run`) |
| Mistake / correction | yes — `record_mistake` / `record_correction` **@agent_tool** | `openTurn.record_*` → `Correction.add(mistake)` |

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
  // ensure_open — plain; not on manifest

Improvement:
  repair: { kind: action, parameters: { tools, asset, violation } }
  verify_fix: { kind: tool, parameters: { tools, theme } }
```

### When things run

```
Prerequisite: BaseContextTool.generate runs workspace.open + turn.ensure_open (prelude — not agent tools)

/generate @agent_instructions (Bdd.generate):
  -> self.workspace.open(); self.turn.ensure_open(self)  // plain
  -> self.decisions.record_decisions_session()
  -> self.contexts, self.examples, self.templates, self.generate_output()  // expand
  -> self.add_generate_header_to_generated()
  -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  // expose finish_turn @agent_tool

/validate — same prelude + host.validate + finish_turn; record_* optional after

Turn.record_mistake / record_correction @agent_tool — post-validate agent choice
```

### Call chain (mistake)

```
Agent
  -> Turn.record_mistake(tools, artifact, rule, wrong, original, tool, fidelity)  @agent_tool
    for host in tools:
      -> openTurn = host.workspace.openTurn or Turn(workSession=host.workspace)
      -> openTurn.record_mistake(mistake)
      -> mistake.persist(host.workspace)
      -> host.workspace.repairs.find_or_create(mistake.theme, backlog).nest([mistake])
    <- entry_id
```

### Call chain (correction)

```
Agent
  -> Turn.record_correction(tools, entry_id, improved, how, status)  @agent_tool
    for host in tools:
      -> openTurn = host.workspace.openTurn or Turn(workSession=host.workspace)
      -> openTurn.record_correction(mistakes, correction)
           // fixedIn = openTurn; each mistake: correction.add(mistake)
      -> correction.persist(host.workspace)
      -> Repair.nest(mistakes)
    <- entry_id
```

### Logging (replaces `@log`)

**`SessionLog.append(...)`** — own workspace package class. **Expand:** framework on `@agent_instructions` expand. **Run:** explicit call at end of auditable recipe bodies. Not `@agent_tool`. Retire `@log` decorator and runner run hooks (see §4).

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
| Mistake / correction | yes — `Turn.record_mistake` / `Turn.record_correction` **@agent_tool** | `openTurn.record_mistake`; `openTurn.record_correction` → `Correction.add(mistake)` each |

**One Turn class** — **@agent_tool** fans out; domain methods on `openTurn`.

Auditable `@agent_instructions`: framework logs **expand**; author logs **run** at end of body.

**Typical `/generate` expansion:**

```
Bdd.generate() @agent_instructions
  -> self.workspace.open()                   // plain
  -> self.turn.ensure_open(self)             // plain
  -> self.decisions.record_decisions_session()
  -> self.contexts, self.examples, self.templates, self.generate_output()  // expand
  -> self.add_generate_header_to_generated()
  -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  // expose finish_turn @agent_tool

Bdd.validate() @agent_instructions
  -> self.workspace.open(); self.turn.ensure_open(self)
  -> self.contexts; self.scan()
  -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  // expose finish_turn @agent_tool
```

---

## 7. Cross-module interaction (target)

```
Bdd.generate() @agent_instructions
  -> self.workspace.open(); self.turn.ensure_open(self)
  -> … domain expand steps …
  -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  // expose finish_turn @agent_tool

Bdd.validate() @agent_instructions
  -> self.workspace.open(); self.turn.ensure_open(self)
  -> self.contexts; self.scan()
  -> SessionLog.append(toolset, name, summary, ok, error=..., payload=...)  // plain — run; not @agent_tool
  // expose finish_turn @agent_tool

Turn.record_mistake(tools, ...) @agent_tool
  -> openTurn.record_mistake(mistake)

Turn.record_correction(tools, ...) @agent_tool
  -> openTurn.record_correction(mistakes, correction)
     // correction.add(mistake)

Improvement.repair(tools, asset, violation) @agent_instructions
  for host in tools:
    -> repair = host.workspace.repairs.for_violation(asset, violation)
    -> repair.open(host, asset, violation)

Improvement.verify_fix(tools, theme) @agent_tool
  -> repairs[theme].verify_fix() -> bddEvals on Repair
```

**Seam rules**

- **GitRepo** — git-shaped surface: `branch` setter switches to an **existing** ref; `create_branch` creates ref only (internal); `checkout_or_create` creates if missing then sets `branch`.
- **WorkSession** — `session_branch`, `scope_paths`, `dirty` as properties; holds `openTurn` (**Turn** instance), turn index, repairs backlog.
- **Turn** — one class: agentic kit *and* `WorkSession.openTurn`. **`ensure_open` plain**; **`finish_turn` / `record_mistake` / `record_correction` `@agent_tool`**. Logging is **`SessionLog`** (workspace package), plain run — not on Turn kit.
- **Mistake** / **Correction** — `Correction.add(mistake)` adds to `correction.mistakes` and sets `mistake.correction`; `persist` after adds.
- **Repair** (domain) — themed bucket with `open`, `verify_fix`, `nest`, `finish`; holds optional `tools_git GitRepo`.
- **Improvement** — thin `/repair` orchestrator over domain Repair resources; no runner/loop type.
- No EvalSession / `host.eval`.

---

## 8. Slash alignment (target)

```
generate | validate | satisfy | document
  -> Bdd.generate | Bdd.validate | … @agent_instructions on BaseContextTool
     -> workspace.open + turn.ensure_open  // plain
     -> domain body                         // expand
     -> finish_turn                         // expose @agent_tool
  // delete HostLifecycle kit; revert agent_skills kit-owned routing for generate/validate/…

repair
  -> Improvement.repair(tools, asset, violation) @agent_instructions

record_mistake
  -> Turn.record_mistake(tools, …) @agent_tool

record_correction
  -> Turn.record_correction(tools, …) @agent_tool

turn
  -> Turn.finish_turn(tools, prompt, result, context) @agent_tool
```

---

## 9. Refactor slices (order)

1. **Annotations** — only `@agent_instructions` / `@agent_tool`; drop `@log`; explicit **`SessionLog.append(...)` plain run** in method bodies; legacy `@action` / `@tool` aliases until migrated.
2. **Naming** — `Session`→`WorkSession`; drop `EvalSession` / `Session=EvalSession`; domain **Repair** vs toolsets **Turn** + **Improvement**.
3. **Session prelude** — `WorkSession.open` plain (fold ensure/create/index/record_root); drop session `@agent_tool`s and host forwards; **`Turn.ensure_open` plain**; **`finish_turn` `@agent_tool`**.
4. **GitRepo seam** — rename `WorkspaceRepo` → `GitRepo`; drop `ensure_session_branch` / `commit_on_session_branch` / `CDDRepo extends`.
5. **Turn on WorkSession** — `openTurn` is a **Turn** instance; commit in `Turn.finish`.
6. **Resources** — domain `record_*` on openTurn; Mistake/Correction `persist`; domain **Repair** with `open` / `verify_fix` / `nest` / `finish`.
7. **BaseContextTool lifecycle** — prelude **run** + domain **expand** + `finish_turn` **expose** on host `generate` / `validate`; **delete HostLifecycle** kit and kit-owned slash routing for lifecycle actions.
8. **Bind at open** — `WorkSession.open()` on each host; delete `_bind_eval` / `host.eval`.
9. **Turn** + **Improvement** — delete host eval forwards and eval `Repair` toolset.
10. **Host slim** — domain `@agent_instructions` only; no session/turn/repair re-exports.
11. **Specs** — agent BDD: generate prelude summary replaces `ensure_session` / `read_context_index` in expansion **tools** list.

### Workspace module checklist

1. Rename `Session` → `WorkSession`; delete `WorkspaceSession` alias.
2. **`open` plain** — fold `ensure_session` / `create_session` / `read_context_index` / `record_context_root`; drop their `@agent_tool` annotations.
3. Rename `WorkspaceRepo` → `GitRepo`; `branch` property (set = switch); internal `create_branch`; `checkout_or_create`.
3. Move branch policy to `WorkSession.session_branch` property; dirty via `WorkSession.dirty`.
4. `Turn.finish` uses `commitMessage`; calls `workSession.git.commit(scope_paths, message)`.
5. **SessionLog** — keep as own workspace class; drop `@log` / runner run-branch / **`control`**; **`append` → events.log + openTurn.toolCalls** for **expand** (framework) and **run** (explicit); add **`role`** metadata; extend **ToolCall** with `ok`, `error`, `role`.
6. Update `workspace-ce.drawio` + `module-context.md`.

### Eval module checklist

1. Delete `EvalSession` turn ownership — move Turn/TurnCommit to WorkSession.
2. **Mistake**, **Correction**, **Repair** (domain resources) stay in eval package; persist via WorkSession.save/load.
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
