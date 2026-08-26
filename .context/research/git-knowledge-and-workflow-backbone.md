# Git as knowledge and workflow backbone

Single plan for CDD workspace, sessions, eval traceability, kanban workflow (ticket
**creation**, GitHub Issues/PRs/Actions, themes), gap coverage (G-01–G-37), tooling
extensions, and external tools — with maximum out-of-box Git and minimal custom code.

**Status:** design proposal (Aug 2026)  
**Related:** `context_tools/actions/workspace/.context/module-context.md`,
`eval-consolidate-workspace/workspace-bdd-sketch.md` (Git-primary association),
`git-primary-association-proof.md`

**Example session** (used in examples below): `eval-consolidate-workspace` on
`session/eval-consolidate-workspace`; mistake `m001` on introducing SHA `3cea46d0`;
correction `05edfa3`.

---

## 1. Vision

Git becomes the **knowledge backbone** and **workflow backbone** for everything
done in **Workspace** and **WorkSession**:

- Versioning and history (turn commits on session branches)
- Eval traceability (mistakes ↔ corrections ↔ introducing commits)
- Tool/action/fidelity/prompt metadata and **context package** (what the agent read)
- Pull requests, tickets, and workflow state (kanban-oriented views)
- Themes, RCA, and analysis (graph queries over the same data)

Nothing replaces git as the canonical store. Views (GitLens, HTML catalog, kanban)
are **projections** — regeneratable from git.

Industry consensus (2025–2026): **code versioning ≠ agent provenance**. Separate:

1. **Artifact state** (git tree) — what landed  
2. **Execution trace** (spans) — ordered causal steps  
3. **Context package** (manifest) — what was eligible to influence the model  
4. **Verification evidence** — why we believed it was OK  

---

## 2. What git commits alone cannot answer

| Question | Commit alone? |
| --- | --- |
| What did the agent *see* when it decided? | No |
| Which instructions/manifest/skills were active? | No |
| Which model/runtime executed the step? | No |
| Why was this change made (intent vs implementation)? | Partial (subject line) |
| How was correctness checked before we trusted it? | No |
| What was tried and rejected? | No |
| Can we replay or audit this decision in six months? | Partial |

**Critical insight:** `Turn.prompt` records what the human/agent *said*, not the
**context package** — expanded instructions, `.context/*.md`, examples, skills —
which can be orders of magnitude larger than the prompt field.

---

## 3. Jobs the agentic delivery engine needs

| Job | Example | Consumers |
| --- | --- | --- |
| **Versioning** | What changed in this turn? | Human diff, CI, agents |
| **Turn envelope** | tool, action, fidelity, prompt, result | Agents replaying intent |
| **Context package** | which `.context/`, manifest, skills were in scope | Replay, audit, judge |
| **Causal trace** | expand → run → commit span tree | Debug, observability |
| **Eval graph** | mistake → introducing → correction | RCA, themes, judge |
| **Verification** | validate/scan/judge pass linked to SHA | Trust, compliance |
| **Intent / requirements** | story, scenario, grill tick, ticket | Humans, audit, kanban |
| **Workflow** | ticket state, PR link, review, merge | Kanban, humans, agents |
| **Platform linkage** | CDD/tools clone, session branch, cross-repo SHA | Repair, eval |
| **Archive / promotion** | session folder + commit range in eval corpus | Ring 5 learning |
| **Handoff / delegation** | subagent context transfer | Multi-agent sessions |

Per-gap **CDD extensions**, **external tools**, and **phases**: **§11**.  
Worked **examples (ASCII)**: **§12**.

### Already locked in CDD (workspace BDD sketch)

| Artifact | Mechanism |
| --- | --- |
| Turn commit | `{tools}-{action}-{fidelity}-{format}` on `session/{name}` branch |
| Mistake | Git **note** on **introducing** SHA (`refs/notes/eval-mistakes`) |
| Correction | Fix commit + **trailers** + note on fix SHA |
| `events.log` | Expand/run audit only — **not** association store |
| `session.yaml` | Bootstrap only — **not** mistake index |

---

## 4. Design principles

1. **Git-primary** — association on the branch graph, not parallel YAML indexes.  
2. **Layered storage** — notes vs trailers vs refs vs committed index per job.  
3. **Materialized views** — JSONL/HTML/kanban are **derived**; regen from git.  
4. **Human + AI parity** — parseable from `git log`, notes, or one index file per session.  
5. **Kanban is a view** — columns are workflow **state**, not a second database.  
6. **Out-of-box first** — GitLens, Git Graph, `gh`; custom code for graph/kanban export.

---

## 5. Four-layer architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  L4  Views — GitLens, Git Graph, catalog HTML, kanban (generated) │
├──────────────────────────────────────────────────────────────────┤
│  L3  utilities/trace_graph — build_eval_graph, regen_*_index      │
├──────────────────────────────────────────────────────────────────┤
│  L2  turn-index.jsonl, workflow-index.jsonl, spans.jsonl,      │
│      context-package.yaml (per turn, under session folder)       │
├──────────────────────────────────────────────────────────────────┤
│  L1  GIT — session commits, notes, trailers, refs/cdd/* (future)│
│      ticket create/link, Workflow-State transitions, PR↔SHA     │
│      (GitHub Issues/PRs/Actions are linked here — not stored)   │
└──────────────────────────────────────────────────────────────────┘
```

**Rule:** If index and git disagree, **git wins**. Run `regen_session_index(session)`.

### Data placement

| Data | Canonical (L1) | Cache (L2) | Audit |
| --- | --- | --- | --- |
| File changes | commit tree | — | `git show` |
| Turn identity | commit subject | turn-index.jsonl | — |
| Prompt / result / tools | commit body | turn-index.jsonl | events.log |
| Context package | yaml per turn | hash in turn-index | — |
| Mistake | note on introducing SHA | turn-index.jsonl | — |
| Correction | fix commit + trailers + note | turn-index.jsonl | — |
| Causal steps | spans.jsonl | regen from events.log | events.log |
| Ticket identity + create event | first turn commit + workflow note; optional `refs/cdd/tickets/*` | workflow-index.jsonl | `gh issue create` body |
| Workflow state transitions | `Workflow-State:` trailer on each turn | workflow-index.jsonl | GitHub Project column *(read-only)* |
| GitHub Issue link | `GitHub-Issue:` trailer (repo#num) | workflow-index.jsonl | `gh issue view` |
| PR link + open/merge | commit trailers on turn + merge commit | workflow-index.jsonl | `gh pr`; GitHub PR UI |
| CI / Actions result | `Verified-By:` / `Checks-Pass:` on validating turn | — | GitHub Checks API / `gh pr checks` |
| Kanban column | derived from `Workflow-State` in git | board JSON | GitHub Projects *(optional mirror)* |

---

## 6. Storage mechanism comparison

| Mechanism | Versioning | Turn metadata | Mistake→fix | Workflow | Agent-parse | Human UI | Retroactive |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Git notes** | — | weak | **best** | good | medium | OK w/ GitLens | **best** |
| **Commit trailers** | **best** | **best** | good | good | **best** | **best** | poor |
| **JSONL index** | — | good | good | **best** | **best** | good | regen only |
| **Custom refs** | — | good | good | **best** | medium | poor | good |
| **session.yaml index** | — | medium | **bad** | medium | medium | medium | drifts |
| **External DB** | good | good | good | good | good | needs UI | N/A |

**Recommendation:** hybrid — not one mechanism.

---

## 7. Turn commits (every `Turn.finish`)

**Subject (done):** `Turn.name` → `{tools}-{action}-{fidelity}-{format}`.

**Body template (implement — G-02):**

```
Turn-Id: a1b2c3d4
Session: eval-consolidate-workspace
Tools: stories,bdd
Action: iterate
Fidelity: development

Prompt: log correction — workspace sketch hierarchy
Result: three mistakes fixed; path resolve then openWorkSession

Context-Package: .context/sessions/.../turns/a1b2c3d4/context-package.yaml
CDD-At: abb39bd
Ticket: CDD-42
GitHub-Issue: abd-context-driven-delivery#87
Workflow-State: specification
Story: workspace-open-turn
Scenario: that-records-a-mistake-on-its-open-turn
```

Corrections add: `Fixes-Mistake:`, `Introducing-Commit:`.  
PRs add: `Pull-Request:`, `Pull-Request-URL:`, `Fixes-GitHub-Issue:` (optional).  
Validate passes add: `Verified-By:`, `Eval-Pass:`, `Judge-Verdict:`.  
Merge adds: `Reviewed-By:`, `Approved-By:`, `Checks-Pass:` (optional).

---

## 8. Tickets, GitHub workflow, and kanban

### 8.1 Two systems, one spine

CDD uses **git as the provenance spine**; GitHub is the **team workflow surface**.
They are not competing stores — each owns what it does best.

| Concern | Canonical (L1 git) | Live / team UI (GitHub) |
| --- | --- | --- |
| *When* did work on ticket X happen? | Turn commits with `Ticket:` + `Workflow-State:` | Issue timeline (derived) |
| *What* SHA introduced the mistake? | eval-mistakes note | — |
| *Who* owns the ticket today? | optional `Assignee:` trailer at handoff | Issue assignee (`gh issue edit`) |
| PR ready to merge? | merge commit + `Reviewed-By:` trailers | PR checks, reviews, merge button |
| Kanban column | last `Workflow-State:` on ticket's turn chain | GitHub Project column *(optional)* |

**Rule:** Git records **decisions and associations at commit time**. GitHub holds
**live collaboration state** (comments, review threads, check runs). Query GitHub
with `gh`; never treat GitHub as the only copy of agent provenance.

### 8.2 Creating tickets (L1)

Tickets enter the system in one of three ways — all must land a **git anchor**
(a commit, note, or ref) so agents and humans can find them without GitHub API.

**A — Create from CDD (recommended when GitHub remote exists)**

```
Human/agent:  /workspace ticket create "Git notes team fetch on deploy"
                    │
                    ▼
CDD:  gh issue create --title "..." --body "Session: eval-…\nStory: …"
                    │
                    ▼
Git:  first turn commit on session branch
      Ticket: CDD-42
      GitHub-Issue: abd-context-driven-delivery#87
      Workflow-State: backlog
      Story: workspace-git-notes-deploy
                    │
                    ▼
Note: refs/notes/cdd-workflow on anchor SHA (optional)
      { "ticket": "CDD-42", "github_issue": 87, "state": "backlog" }
```

**B — Link existing GitHub issue**

```
Human already filed #87 on GitHub
      │
      ▼
CDD:  /workspace ticket link 87
      │
      ▼
Git:  same trailers on first linked turn commit (no second issue created)
```

**C — Local-only ticket (no GitHub remote)**

```
CDD assigns CDD-42 from session-scoped counter in refs/cdd/tickets/CDD-42
      │
      ▼
Git:  Ticket: CDD-42 + workflow note only (no GitHub-Issue: trailer)
```

Planned CDD surface (Phase 3, G-04 / G-36): `WorkSession.create_ticket`,
`WorkSession.link_issue`, `GitRepo.workflow_note` — thin wrappers around
`gh issue create` / `gh issue view`, always finishing with a turn commit.

### 8.3 Workflow state on the session branch

Each turn that advances a ticket stamps trailers (see §7 body template):

```
Workflow-State: specification    # CDD kanban column
Ticket: CDD-42
GitHub-Issue: abd-context-driven-delivery#87
```

**Kanban columns (default):** `backlog` → `discovery` → `specification` →
`engineering` → `review` → `done`. Custom columns are allowed per workspace;
`trace_graph` projects the **last known state per ticket** from git, not from
GitHub Projects.

```
 BACKLOG          SPECIFICATION         ENGINEERING         REVIEW
 ┌─────────┐      ┌─────────────────┐   ┌──────────────┐   ┌──────┐
 │ CDD-40  │      │ CDD-42          │   │ CDD-41       │   │ CDD-43│
 │ gh #85  │      │ gh #87          │   │ gh #86       │   │ gh #88│
 └─────────┘      │ workspace git   │   └──────────────┘   └──────┘
                  └────────┬────────┘
                           │  every turn: Ticket + Workflow-State trailers
                           ▼
                  workspace-bdd-sketch.md (Story/Scenario anchors)
```

Regenerate board: `regen_workflow_index(session)` → `workflow-index.jsonl` →
kanban HTML (G-34). If git and GitHub Project disagree, **git wins** for CDD
projections; use `gh` only to *sync* GitHub when humans want both aligned.

### 8.4 Pull requests and GitHub Actions

**Opening a PR** (when session work is ready for main):

```
1. Push session branch
2. gh pr create --title "CDD-42: git notes on deploy" \
      --body "Ticket: CDD-42\nFixes #87\nSession: eval-consolidate-workspace"
3. Turn.finish on merge-prep turn adds trailers:
      Pull-Request: 42
      Pull-Request-URL: https://github.com/.../pull/42
      Ticket: CDD-42
      Workflow-State: review
```

**GitHub Actions / CI** — checks run on the PR branch. CDD does **not** mirror
full CI logs into git. Instead:

| Event | Stored in L1 git | Queried live |
| --- | --- | --- |
| Local `validate` / `scan` pass before push | `Verified-By:`, `Scan-Result:` on turn commit | — |
| GitHub Actions green on PR | optional `Checks-Pass: pr/42@abc1234` on merge commit | `gh pr checks 42` |
| Human approval | `Reviewed-By:`, `Approved-By:` on merge commit | GitHub review UI |
| Merge to main | merge commit SHA + all trailers | `gh pr view --json mergedAt` |

**Closing the loop:** merge commit should repeat `Ticket:`, `GitHub-Issue:`,
and set `Workflow-State: done`. Optionally `gh issue close 87 --comment "Merged in …"`.
GitHub's native `Fixes #87` in the PR body auto-closes the issue; CDD trailers
make the same link **searchable in `git log`** without API calls.

### 8.5 What GitHub workflow is *not* in L1

Do **not** put these in git as canonical stores:

- Issue comment threads (use GitHub; link milestone SHAs in comments if needed)
- PR review line comments (GitHub only)
- Actions run logs (GitHub Checks; store pass/fail **verdict** as trailer only)
- GitHub Project custom fields (mirror optional; git `Workflow-State` is SoT for CDD kanban)

Future optional integration (Phase 3+): a GitHub Action triggered on `push` to
`session/*` that posts turn summary to the linked issue — **notification only**,
not a second index.

### 8.6 Evolve storage when listing gets slow

**Start:** ticket trailers + `refs/notes/cdd-workflow` notes on anchor SHAs.  
**Evolve:** `refs/cdd/tickets/CDD-42` → `{ github_issue, session, anchor_sha, state }`
when kanban needs fast listing without walking full branch history.  
**Kanban UI:** L3 `trace_graph` → HTML (catalog chrome) — never `session.yaml`
as workflow SoT.

---

## 9. Mistakes and corrections (keep)

| Event | Store |
| --- | --- |
| **Mistake** | Note on **introducing** SHA |
| **Correction** | Fix commit; note on fix SHA; `fixed_by` on introducing note |

Do **not** use `session.yaml` or `mistakes/` folders as graph store (human repair
artifacts only).

---

## 10. Prior art — borrow pieces, avoid NIHS and avoid wrong adoption

Other teams have already tackled parts of agent traceability, git-native metadata,
and workflow linkage. This section answers three questions honestly:

1. **Who has done something similar?**
2. **Why don't we just use their tool?**
3. **What specific pieces should we take?**

**Rule:** Git + session files remain canonical (§4). External tools are vocabulary,
hooks, or optional complements — not a second spine.

### 10.1 Academic / pattern receipts (research papers)

These informed CDD's *shape* but are not products to install.

| External idea | Problem it solves | CDD equivalent | Use their product? |
| --- | --- | --- | --- |
| Braintrust / MLflow **spans** | Ordered causal steps (expand → run → commit) | `spans.jsonl` (G-11) | No — same shape, our files |
| **PROV-AGENT** vocabulary | Standard names for turns, tool calls, prompts | Turn → ToolCall in commit body and index | No — borrow vocabulary only |
| **ContextNest** | Audit what context the model *could* have seen | `context-package.yaml` per turn (G-06) | No — git yaml sidecar |
| **Code Digital Twin** | Graph / dashboard over code and history | `build_eval_graph` + catalog HTML (G-33) | No — generated from git |
| **Agile V** evidence bundle | One folder that proves a delivery episode | `.context/sessions/{name}/` on session branch | No — already git files |
| **Loom** (jsuppe) requirements | Link requirements to changes over time | `Story:`, `Scenario:`, `Rationale:` trailers | No — not Loom's SQLite DB |
| **Axiom** five-layer chain | Intent → design → code → test → deploy | Same chain as trailers across turns | No — git timeline |
| **Bitloops** audit checklist | “Can you prove X?” governance questions | §11 gap matrix + commit body | No — checklist in this doc |

### 10.2 Git-native tools doing the same *kind* of thing

These are the closest real implementations. None cover CDD's full job (session turns,
eval mistake graph, context package, BDD/grill workflow, kanban + GitHub bridge).

| Project | What it stores | Mechanism | Overlap with CDD | Gap vs CDD |
| --- | --- | --- | --- | --- |
| [**agit**](https://github.com/Madhurr/agit) | Agent *why*: intent, alternatives, risks, test results | `refs/notes/agit` JSON per commit | Notes on commit; `alternatives_considered` ≈ G-14 | No session branch, eval graph, context package, tickets |
| [**git-ai**](https://github.com/git-ai-project/git-ai) | Line-level *who wrote which line* + model/prompt link | Git notes; prompt store **outside** git | Notes survive rebase/merge (important for session branches) | Attribution ≠ delivery workflow; prompts off-repo; no eval/mistake graph |
| [**agentdiff**](https://github.com/codeprakhar25/agentdiff) | Signed line attribution across agents | Hooks + `refs/agentdiff/traces/*` | Agent Trace v0.1 interop; fetch refspec pattern | Audit/compliance focus; no turns, stories, or kanban |
| [**Lore**](https://github.com/meredian-labs/lore) (tool) | Engineering *why* via hooks + agent recaps | `.lore/lore.db` (SQLite) + git hooks | “Decision shadow” problem; `lore why <file>` | **SQLite SoT** — conflicts with git-primary; no eval graph |
| [**Lore**](https://arxiv.org/html/2603.15566v1) (paper) | Structured decision records in commits | Git **trailers** only | Direct validation of commit-body approach (G-02, G-14) | No session/workflow model |
| [**git-meta**](https://git-meta.com/) | Typed metadata on commits, paths, branches | `refs/meta/*` commits | Fine-grained refs when notes get crowded | New ref namespace + tooling; no CDD domain |
| [**git-native-issue**](https://github.com/remenoscodes/git-native-issue) | Issues entirely in git | `refs/issues/*` commit chains + `State:` trailers | Local ticket without GitHub (G-36 option C) | No agent turns, eval, or context package |
| [**Transcript binding RFC**](https://github.com/theagenticguy/claude-sql/blob/main/docs/rfc/0001-transcript-pr-binding.md) | Bind commit ↔ agent transcript | Trailers **+** `refs/notes/transcripts` (dual surface) | Redundant trailer+note pattern; PR binding | Transcript store, not delivery/eval workflow |
| [**tracker-hook**](https://github.com/smolijar/tracker-hook) | Auto issue ref from branch name | `Related:` trailer in prepare-commit-msg | Branch → ticket trailer automation | Hook only; no session or eval model |

**SaaS / DB observability** (different layer — runtime traces, not delivery provenance):

| Project | What it stores | Why not as CDD spine |
| --- | --- | --- |
| **Langfuse** / **Braintrust** / **MLflow** | OTel spans, LLM I/O, eval scores in DB | Great for *live* debugging and cost; not versioned with the code diff; doesn't answer “which `.context/` file did the agent read at this SHA?” |
| **GitHub Copilot OTel → Langfuse** | Agent spans with git branch/SHA context | Useful **complement** (G-15 runtime); git still holds durable verdict and association |

### 10.3 Why we don't just adopt one of them

| If we adopted… | We'd gain | We'd lose or still have to build |
| --- | --- | --- |
| **agit** only | Rich “why” notes on every commit | Session branches, `Turn.name`, eval mistake↔fix graph, context-package, BDD/grill, kanban |
| **git-ai** only | Line attribution + rebase-safe notes | Same gaps; plus prompts live outside repo (access control tradeoff we may want differently) |
| **Lore (tool)** only | Nice `why` queries and hooks | SQLite becomes second SoT; drift from session branch; no eval ring model |
| **git-native-issue** only | Pure-git tickets | GitHub team workflow, agent turn envelope, eval, context package |
| **Langfuse** only | Best-in-class span UI | Nothing durable in git for audit in six months without that service |
| **GitHub Issues alone** | Team kanban everyone knows | No agent context package, no mistake-on-introducing-SHA, no turn replay |

**CDD's differentiator** is not “store metadata in git” (many tools do that). It is
the **delivery model**: WorkSession → Turn → session branch commit → eval graph →
`.context/` context package → story/grill/ticket trailers → regen indexes from git.

No single prior art tool implements that stack. Adopting one wholesale would mean
either abandoning eval/session semantics or running two spines that drift.

### 10.4 What we should borrow (concrete)

Actionable imports — implement inside CDD, not as mandatory third-party deps.

| Borrow from | Take this | CDD landing | Phase |
| --- | --- | --- | --- |
| **agit** schema | `alternatives_considered`, `key_decisions`, `risks`, `unknowns` | G-14 `Rationale:` / `Rejected:` in turn commit body | 3 |
| **Lore (paper)** | Commit message as structured decision record; trailer vocabulary | G-02 body template; standard trailer keys | 1 |
| **Transcript RFC** | Dual surface: human trailers + JSON note; digest agreement check | eval-mistakes note + `Fixes-Mistake` trailer (already); add integrity check for ticket/issue binding | 2 |
| **git-ai** | Note merge behavior across rebase/cherry-pick | Document + test `regen_*_index` after rewrite; consider note-copy helper in `GitRepo` | 2 |
| **git-ai / agentdiff** | Fetch refspec for custom refs/notes on clone | Extend `configure_git_notes` → `+refs/cdd/*:refs/cdd/*`, `+refs/notes/*:refs/notes/*` (G-35) | 1 |
| **agentdiff** | Agent Trace v0.1 field names where they overlap | Optional export block in `context-package.yaml` for interop | 3 opt |
| **git-native-issue** | `refs/issues/*` + `State:` on commit chain | Local-only ticket path when no GitHub (G-36 C) | 3 |
| **tracker-hook** | Branch name → `Ticket:` / `GitHub-Issue:` trailer | `session/{name}` branch convention → auto trailer on `Turn.finish` | 3 |
| **Gerrit / kernel** | `Change-Id:`, `Signed-off-by:` trailer patterns | `Reviewed-By:`, `Verified-By:`, duplicate-key trailers | 2–3 |
| **Langfuse / OTel** | GenAI span semantics (model, tokens, tool name) | Optional **export** from Cursor/SDK to `spans.jsonl` — not stored in Langfuse as SoT | 5 opt |
| **PROV-AGENT** | Entity/relation names (Agent, Activity, Entity) | `build_eval_graph` JSON-LD export | 4 opt |

**Do not adopt as primary store:** Lore SQLite, Braintrust/MLflow/Langfuse DB, Loom
SQLite, git-ai cloud prompt store, or any system where the audit trail cannot be
reconstructed from `git clone` + session folder.

**Optional complement (not NIHS — different job):** self-hosted Langfuse or Copilot
OTel export for *during-session* debugging; on-finish export of **summary span**
into `spans.jsonl` on the session branch so git remains the long-term record.

### 10.5 Sanity check — are we reinventing wheels?

| Concern | Reinventing? | Verdict |
| --- | --- | --- |
| Git notes for metadata | agit, git-ai exist | **No** — we reuse notes; our *schema* is eval/workflow-specific |
| Commit trailers | Lore paper, kernel decades | **No** — standard git feature |
| Span tree | Braintrust, Langfuse | **Partially** — same *idea*; file format is ours tied to `SessionLog` |
| Context package audit | ContextNest paper | **Partially** — no off-the-shelf tool reads `.context/` + manifest |
| Eval mistake graph | Unique to CDD eval ring | **Yes, intentionally** — no prior art found for note-on-introducing-SHA + fix trailer |
| Session branch turns | Unique to CDD workspace | **Yes, intentionally** — product model, not generic git tooling |
| Kanban + GitHub | GitHub Projects, Jira | **No** — we delegate live UI to GitHub; git holds state transitions |

**Bottom line:** CDD is not ignoring prior art. It combines proven git primitives
(notes, trailers, refs) with a delivery-specific model eval and workspace already
committed to. Borrow schemas and hook patterns; don't bolt on a second database or
replace the session-branch turn model with a generic agent hook.

---

## 11. Gap coverage matrix

For each gap: **CDD tooling extension**, **artifacts**, **external tools**, **phase**.

### CDD packages

| Package | Role |
| --- | --- |
| `context_tools/actions/workspace` | Turn, WorkSession, SessionLog, GitRepo, ContextIndex, ContextPackage *(new)* |
| `context_tools/actions/workspace` | WorkSession, Turn, Mistake, Correction, GitRepo |
| `context_tools/base` | validate/scan finish → verification trailers |
| `context_tools/bdd` | agent_bdd judge, regression anchors |
| `primitives/actions` | expand → SessionLog/SpanLog |
| `primitives/tools` | manifest paths |
| `utilities/agent_skills` | deploy, `configure_git_notes`, team `.vscode` settings |
| `utilities/handoff` | handoff payload + span |
| `utilities/catalog_generator` | HTML shells (catalog, kanban) |
| `utilities/trace_graph` *(new)* | `build_eval_graph`, `regen_*_index` |

### External tools (team baseline)

| Tool | Role in CDD |
| --- | --- |
| **GitLens** | Primary: graph, search, blame, `${notes}`, PRs |
| **Git Graph** | Branch topology, cherry-pick, compare mistake/fix |
| **Git Notes** (jrosco) | Notes inventory, fetch/push (optional) |
| **Vanilla SCM / Timeline** | Quick diff; file history |
| **`gh` CLI** | Issue create/view/close; PR create/checks/merge; Project list |
| **GitHub Actions** | CI on PR; optional session-branch notify (future) |
| **GitKraken Desktop** | Optional multi-repo graph |

### Core jobs

| ID | Gap | CDD extension | Artifacts | External tools | Phase |
| --- | --- | --- | --- | --- | --- |
| G-01 | Versioning | `Turn.finish` → `GitRepo.commit` | session-branch commits | GitLens diff, SCM, Git Graph | **0** ✓ |
| G-02 | Turn envelope | `Turn.finish` body builder | Prompt, Result, Turn-Id trailers | GitLens `${message}` search | **1** |
| G-03 | Eval graph | `record_mistake`, `record_correction`, `GitRepo.note` | eval-mistakes notes; Fixes-Mistake | GitLens `${notes}`; Git Notes list | **0** ✓ |
| G-04 | Workflow state | `Workflow-State:` on each turn; workflow notes | trailers + cdd-workflow notes | kanban HTML; GitHub Projects *(mirror)* | **3** |
| G-05 | Platform linkage | `CDDRepo`, `cddAt`, WorkSession branch | CDD-At; branch@sha in index | Git Graph session lane | **1** / **4** |
| G-36 | Ticket create/link | `WorkSession.create_ticket`, `link_issue`; `gh issue create` | Ticket + GitHub-Issue trailers; anchor note | `gh issue`; GitHub Issues UI | **3** |

### Context & instructions

| ID | Gap | CDD extension | Artifacts | External tools | Phase |
| --- | --- | --- | --- | --- | --- |
| G-06 | Context package | `ContextPackage.capture` at open/finish | `context-package.yaml` per turn | GitLens shows Context-Package trailer | **1** |
| G-07 | Manifest version | manifest cmd + toolset blob SHA in package | Manifest-SHA in yaml/trailer | GitLens blame at SHA | **1** |
| G-08 | Skill/rule surface | deploy-state + rules paths in package | skills_deployed, rules_surface | diff `.deploy-state.json` | **1** |
| G-09 | Point-in-time replay | `regen_context_package(session, sha)` | regen yaml from git | `git show sha:path` | **2** |
| G-10 | Retrieval evidence | *Defer* optional `retrieval.jsonl` | — | None stable in IDE | **5** |

### Execution & causality

| ID | Gap | CDD extension | Artifacts | External tools | Phase |
| --- | --- | --- | --- | --- | --- |
| G-11 | Causal graph | `SpanLog` + expand hooks | `spans.jsonl` | `build_eval_graph` Mermaid | **1** |
| G-12 | Run identity | single `tools.ps1 run`/turn; `run_id` at open | run_id in index/spans | — | **1** |
| G-13 | Handoff | extend `utilities/handoff` | `handoff-payload.yaml` + span | — | **2** |
| G-14 | Rationale/rejected | design-turn `Rationale:`/`Rejected:` in body | commit body | GitLens search | **3** |

### Runtime

| ID | Gap | CDD extension | Artifacts | External tools | Phase |
| --- | --- | --- | --- | --- | --- |
| G-15 | Model/runtime | optional block in context-package | runtime.agent/model | Cursor SDK (future) | **3** opt |
| G-16 | Toolchain/env | env_hash in package | tools.ps1, venv, requirements | `setup.ps1` / `tools.ps1` | **1** |
| G-17 | Token/cost | *Defer* | — | — | **5** |

### Intent

| ID | Gap | CDD extension | Artifacts | External tools | Phase |
| --- | --- | --- | --- | --- | --- |
| G-18 | Story/scenario/grill | Story, Scenario, Grill-Tick trailers | turn-index | kanban HTML links | **3** |
| G-19 | Design rationale | same as G-14 | commit body | — | **3** |
| G-20 | Ticket link | overlaps G-04, G-36 | Ticket + GitHub-Issue trailers | `gh issue view` | **3** |
| G-37 | PR + CI bridge | `open_pull_request` helper; merge turn trailers | Pull-Request, Checks-Pass, Reviewed-By | `gh pr`; GitHub Actions | **3** |

### Verification

| ID | Gap | CDD extension | Artifacts | External tools | Phase |
| --- | --- | --- | --- | --- | --- |
| G-21 | Pass evidence | validate/scan/judge → `Turn.finish` trailers | Verified-By, Eval-Pass | CI if specs in pipeline | **2** |
| G-22 | Human review | merge commit Reviewed-By/Approved-By | merge body | GitHub PR + GitLens | **3** |
| G-23 | Regression anchor | agent_bdd pass → Regression-Anchor trailer | spec path | re-run mamba locally | **4** |
| G-24 | Scan snapshot | scan action → Scan-Result trailer | commit trailer | — | **2** |

### Lifecycle

| ID | Gap | CDD extension | Artifacts | External tools | Phase |
| --- | --- | --- | --- | --- | --- |
| G-25 | To/from/with | turn-index writer in finish | from/with/to JSON | graph export | **1** |
| G-26 | Cross-repo | `repos_for_workspace` on every turn | change_repo + tool_repo | Git Graph / GitKraken | **1** |
| G-27 | Archive promote | `eval.Archive.promote` | pointer.yaml; refs/cdd/archive | — | **4** |
| G-28 | Session continuity | load + regen; stale context warning | session.yaml bootstrap | GitLens checkout | **2** |

### Analysis

| ID | Gap | CDD extension | Artifacts | External tools | Phase |
| --- | --- | --- | --- | --- | --- |
| G-29 | Theme clustering | graph rollup by rule | HTML theme nodes | dashboard | **4** |
| G-30 | Ring maturity | ring metadata in session.md / skills | convention | — | **1** doc |
| G-31 | Drift detection | context-package hash compare | drift in turn-index | — | **4** |

### Infrastructure

| ID | Gap | CDD extension | Artifacts | External tools | Phase |
| --- | --- | --- | --- | --- | --- |
| G-32 | Index cache | `TurnIndex.append` | turn-index.jsonl, workflow-index.jsonl | agents read jsonl | **1** |
| G-33 | Query/graph | `utilities/trace_graph` | JSON, Mermaid, HTML | Git Graph topology | **2** |
| G-34 | Kanban projection | workflow graph → board HTML | generated page | browser | **3** |
| G-35 | Team git/IDE setup | `configure_git_notes`; `.vscode` GitLens | notes fetch; settings | GitLens, Git Notes | **0** ✓ / **1** |

---

## 12. Gap examples (ASCII, CDD context)

### G-06 — Context package

```
  Human: "Why did sketch say openWorkSession before Turn.open?"

  WITHOUT package                 WITH context-package.yaml
  git show → diff only            git show + yaml @ module-context 7f2e1a
                                  → "agent read OLD context"
```

### G-11 — Causal spans

```
Flat events.log:  expand → expand → run → run
Span tree:        open_turn ─┬─ expand contexts
                             ├─ expand examples
                             ├─ run iterate
                             └─ commit c2ffd3f
```

### G-21 — Verification (success path)

```
  sketch ──► validate ──► merge
              └── Eval-Pass @ abb39bd

  c2ffd3f ──verified_by──► abb39bd
         └──fixes──► 3cea46d0 (mistake m001)
```

### G-07 — Manifest version

```
  bdd.py @ A: "iterate once"     bdd.py @ B: "iterate each tool"
       └── sketch v1                   └── sketch v2
            same Turn.name ── different Manifest-SHA
```

### G-25 — To / from / with

```
  [CDD @ abb39bd] ──with──► bdd.iterate ──► sketch.md ──► commit c2ffd3f
```

### G-27 — Archive promotion

```
Working repo .context/sessions/foo/pointer.yaml ──► Archive repo full session + sha range
```

### G-13 — Handoff

```
  /bdd iterate  ──handoff-payload.yaml──►  /repair improve
         └──────────── span s7 ──────────────┘
```

### G-14 — Rationale / rejected

```
  Option A: yaml index ── rejected (drift)
  Option B: git notes ── chosen
  Option C: tags ─────── rejected (noise)
  → stored on design-turn commit body
```

### G-36 — Ticket create + GitHub issue

```
  /workspace ticket create "Git notes on deploy"
           │
           ├─► gh issue create  ──► GitHub #87 (team UI)
           │
           └─► turn commit c2ffd3f
                 Ticket: CDD-42
                 GitHub-Issue: abd-context-driven-delivery#87
                 Workflow-State: backlog

  Later turn: Workflow-State: specification  (kanban moves card)
  PR turn:    Pull-Request: 42  +  Fixes #87 in gh body
  Merge:      Workflow-State: done  +  Reviewed-By: jeff
```

### G-37 — PR and GitHub Actions

```
  session/eval-* ──push──► gh pr create ──► PR #42
                                │
                    GitHub Actions (validate, scan)
                                │
                    gh pr checks 42  (live — not stored as log)
                                │
  merge commit abb39bd ◄── gh pr merge
      Checks-Pass: pr/42@f8a1b2c
      Pull-Request: 42
      Ticket: CDD-42
      Workflow-State: done
```

---

## 13. External tools — capability matrix

| Tool | Can do (CDD example) | Cannot do |
| --- | --- | --- |
| **GitLens** | Graph session branch; search `Fixes-Mistake`; `${notes}` shows m001; blame workspace.py; PR on merge | Mistake/fix icons from notes; context package |
| **Git Graph** | Cherry-pick correction; diff 3cea46d0 vs 05edfa3 | Notes, kanban, context package |
| **Git Notes** | List/push eval-mistakes notes | Auto-write from Turn; graph columns |
| **SCM / Timeline** | Diff c2ffd3f; file history on sketch.md | Notes, prompts, eval edges |
| **GitKraken** | Multi-repo graph; rebase session branch | Notes, turn metadata, spans |
| **`gh`** | `issue create/view/close`; PR #42 status; `pr checks` | Store provenance or CI logs (git does verdict only) |
| **GitHub Actions** | Run validate/scan on PR; gate merge | Replace git trailers; store full logs in L1 |

### Which tool for which question?

| Question | Today | Target (CDD + external) |
| --- | --- | --- |
| What changed? | `git show`, SCM | same |
| Mistake on which SHA? | `git notes show` | + GitLens `${notes}` |
| What fixed m001? | `git log --grep Fixes-Mistake` | + build_eval_graph |
| What context did agent read? | — | context-package.yaml |
| Order of steps? | events.log | spans.jsonl |
| Why trust this SHA? | — | Verified-By trailer |
| Ticket on board? | — | Workflow-State + kanban HTML |
| Create ticket? | — | G-36: `create_ticket` → gh issue + turn commit |
| PR + CI green? | — | `gh pr checks`; Checks-Pass trailer on merge |

Team git setup (`agent_skills` deploy):

```ini
notes.displayRef = refs/notes/eval-mistakes
remote.origin.fetch = +refs/notes/*:refs/notes/*
```

GitLens (commit to `.vscode/settings.json` in phase 1):

```json
{
  "gitlens.views.formats.commits.label": "${message}",
  "gitlens.views.formats.commits.description": "${notes}"
}
```

---

## 14. CDD-native tools

| Tool | Status | Trigger |
| --- | --- | --- |
| `Turn.finish` | done | end of action turn |
| `Turn.record_mistake` / `record_correction` | done | eval turns |
| `SessionLog.append` | done | expand/run |
| `configure_git_notes` | done | agent_skills deploy |
| `ContextPackage.capture` | planned G-06 | Turn open/finish |
| `SpanLog.append` | planned G-11 | expand/run/open/finish |
| `TurnIndex.append` | planned G-32 | Turn.finish |
| `build_eval_graph` | planned G-33 | tools.ps1 |
| `WorkSession.create_ticket` / `link_issue` | planned G-36 | `/workspace ticket` |
| `open_pull_request` + merge trailers | planned G-37 | session → main |
| `regen_turn_index` | planned G-28/G-33 | after rebase |
| `eval.Archive.promote` | planned G-27 | session close |
| `catalog_generator` | done | static tool catalog |
| `handoff` + payload | planned G-13 | `/handoff` |

---

## 15. Phased roadmap

### Phase 0 — Done

G-01, G-03, G-35 (partial): session branches, Turn.name, eval notes, correction
trailers, `configure_git_notes`.

### Phase 1 — Ring 1 complete (~1–2 days)

| Gaps | CDD work | External |
| --- | --- | --- |
| G-02, G-05, G-16, G-25, G-26, G-32 | commit body; turn-index.jsonl; to/from/with; CDD-At | GitLens search |
| G-06, G-07, G-08 | ContextPackage.capture + yaml per turn | — |
| G-11, G-12 | spans.jsonl; single-process turn in deploy skills | — |
| G-30, G-35 | ring-1 docs; `.vscode` GitLens settings | GitLens team config |

### Phase 2 — Query + trust (~2–3 days)

| Gaps | CDD work | External |
| --- | --- | --- |
| G-09, G-28, G-33 | `utilities/trace_graph`; regen tools | Git Graph compare |
| G-13 | handoff payload + span | — |
| G-21, G-24 | verification/scan trailers on finish | — |

### Phase 3 — Workflow + intent (~1 week)

| Gaps | CDD work | External |
| --- | --- | --- |
| G-04, G-18, G-19, G-20, G-22, **G-36**, **G-37** | ticket create/link; story/grill/PR/CI trailers; workflow notes | `gh issue` / `gh pr`; GitHub Actions; GitLens PR |
| G-14 | Rationale/Rejected on design turns | GitLens search |
| G-34 | kanban HTML from workflow-index | browser; optional GitHub Projects sync |
| G-15 | runtime block in package (optional) | — |

### Phase 4 — Knowledge backbone (~ongoing)

G-27, G-23, G-29, G-31, G-05 full: archive, regression anchors, themes, drift,
cross-session graph.

### Phase 5 — Defer

G-10 (IDE retrieval), G-17 (tokens), G-15 full (model ID without host API).

---

## 16. What not to do

1. Don't use `session.yaml` as turn/mistake index.  
2. Don't tag every turn/mistake.  
3. Don't treat kanban JSON as SoT.  
4. Don't build VS Code icon extensions before graph HTML exists.  
5. Don't store full expanded manifest in commit message — sidecar yaml + hash.  
6. Don't use external DB as primary.  
7. Don't adopt Braintrust/Loom SaaS/DB as SoT — patterns only.

---

## 17. Bottom line

| Layer | Choice |
| --- | --- |
| Versioning | Session-branch commits (`Turn.name`) |
| Turn + context | Commit body + **context-package.yaml** per turn |
| Mistakes | Notes on introducing SHAs |
| Corrections | Fix commits + trailers + notes |
| Fast agent read | turn-index.jsonl (regeneratable) |
| Graph / kanban | trace_graph → HTML/Mermaid |
| Tickets + GitHub | L1 trailers + notes; `gh issue create`; Actions verdict on merge |
| Human browse | GitLens + Git Graph + generated dashboard |

**Highest leverage next:** G-06 context-package + G-32 turn-index (Phase 1).

---

## 18. Open decisions

| Decision | Options | Lean |
| --- | --- | --- |
| Ticket ID | CDD-42 only vs GitHub #87 only vs both | **Both**: `Ticket:` local + `GitHub-Issue:` when remote |
| Ticket storage | notes vs `refs/cdd/tickets` | notes first; refs when listing slow |
| Ticket creation | manual gh vs CDD `create_ticket` | CDD wrapper always finishes with turn commit |
| GitHub Project sync | one-way git→GH vs read-only GH | git `Workflow-State` SoT; optional one-way sync |
| Prompt in index | full vs hash | hash in jsonl; full in commit body |
| Workflow columns | CDD stages vs custom | discovery/spec/engineer + backlog/done |
| PR canonical SHA | merge commit vs last turn | merge commit + trailers |
| CI in git | full log vs pass/fail trailer | **verdict trailer only**; logs stay in GitHub |

---

## References

### CDD
- `context_tools/actions/workspace/.context/sessions/eval-consolidate-workspace/grill-answers.md`

### Papers (patterns)
- [Braintrust — Agent observability 2026](https://www.braintrust.dev/articles/agent-observability-complete-guide-2026)
- [MLflow — Agent observability 2026](https://mlflow.org/articles/what-is-agent-observability-a-2026-developer-guide/)
- [PROV-AGENT](https://arxiv.org/html/2508.02866) · [ContextNest](https://arxiv.org/html/2607.02116v1) · [Code Digital Twin](https://doi.org/10.48550/arxiv.2503.07967) · [Agile V](https://arxiv.org/html/2602.20684v1)
- [Lore — commit trailers as knowledge protocol (paper)](https://arxiv.org/html/2603.15566v1)
- [Axiom audit trail](https://axiomstudio.ai/blog/building-an-ai-audit-trail-from-model-selection-to-production) · [Bitloops audit trails](https://bitloops.com/resources/governance/audit-trails-for-ai-assisted-development) · [Loom requirements (jsuppe)](https://github.com/jsuppe/loom)

### Git-native prior art (§10.2–10.4)
- [agit](https://github.com/Madhurr/agit) · [git-ai](https://github.com/git-ai-project/git-ai) · [agentdiff](https://github.com/codeprakhar25/agentdiff)
- [Lore (tool)](https://github.com/meredian-labs/lore) · [git-meta](https://git-meta.com/) · [git-native-issue](https://github.com/remenoscodes/git-native-issue)
- [Transcript–PR binding RFC](https://github.com/theagenticguy/claude-sql/blob/main/docs/rfc/0001-transcript-pr-binding.md) · [tracker-hook](https://github.com/smolijar/tracker-hook)

### Observability complements (optional, not SoT)
- [Langfuse — OTel backend](https://langfuse.com/docs/observability/sdk/overview) · [GitHub Copilot OTel → Langfuse](https://langfuse.com/integrations/developer-tools/github-copilot)

*Update this file when phases land, prior art shifts, or decisions close.*
