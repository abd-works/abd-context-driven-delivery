# Relationship review, checked against the code

Five agents read the code behind every runtime relationship and every production class, area by area, and confirmed or overturned the first rule-based list in `../repo-model-disconnected.md`. Each line gives the verdict, `file:line` evidence, and for a W the owner, the relationship it should be, and the redesign.

- **R** — right as a runtime dependency: two independent objects, one asks the other to act.
- **W** — wrong shape: the caller builds the other per call from strings or dicts, re-reads what another object holds, or passes an owner's data into a helper; it should be a part or a held collaborator.
- **D** — no use: nothing uses it at run time or build time; delete.

| Area | File | Relationships | R | W | Overturned | Classes | D |
|---|---|---|---|---|---|---|---|
| harness core (name, annotations, process, markdown, agent_tools, installation, hooks, mcp) | [harness-core.md](harness-core.md) | 147 | 93 | 52 | 26 | 158 | 2 |
| harness upper (guidance, guidance_actions, graph, diagnostics, catalog, design_canvas, chat) | [harness-upper.md](harness-upper.md) | 164 | 101 | 56 | 20 | 137 | 5 |
| space and tools | [space-tools.md](space-tools.md) | 131 | 80 | 51 | 20 | 69 | 1 |
| actions and patterns | [actions-patterns.md](actions-patterns.md) | 85 | 50 | 35 | 2 | 72 | 1 |
| practices | [practices.md](practices.md) | 394 | 225 | 169 | 16 | 396 | 10 |
| **Total** | | **921** | **549** | **363** | **84** | **832** | **19** |

## D — no use, delete (19 classes)

- harness: `Agent`, `AgentGuidance` (no `@agent`/`@agent_guidance` anywhere); `FixtureScreen`, `ScenarioSource`, `CanvasVersions`, `PublishedVersion` (design_canvas); `ProjectRulesets` (spec-only).
- tools: `ActionInspector` (an `_examples` toolset nothing loads).
- patterns: `LernCanvasFixtures`.
- practices: `File`; `UpdateReport`, `Change`, `ChangeKind`; `DomainModelLinks`; `_Background`, `StoryNodeTransformer`, `StoryExampleCollector` (an unread seed copy); `AgentSpecManifest`, `read_manifest`; `OutputFolder` (only the two channel feature specs use it — keep if those specs stay).
- Unused members of used classes: listed in each file (e.g. `ContextSetup`'s four practice fields, `Loop.inject`, `SessionLog.append_chat`).

## The W themes that cover most of the 363

1. **Objects rebuilt on every call instead of held as parts** — AgentToolSet's tools, Markdown's text, Repo's Git/Worktrees, Session's Repo/Handoffs/DecisionRecords, Board's tickets, Format built from strings, each installation's IdeLayout.
2. **Things passed around as name strings and looked up again** — toolsets as `module:Class` strings, practices looked up by name in the graph, a fidelity's stage as a string, practices as key strings in validate.
3. **One file with several owners or readers** — `.sessions/session.json` (four `WorkState` owners), the schema files (three readers), the main clone rebuilt from paths in about six places.
4. **Format adapters that wrap or copy the domain model instead of subclassing it** (practices).
5. **Doer and helper classes doing an owner's work** — graph helpers, validate helpers, a `ToolCall` built only to find a session.

## Defects found along the way

- `MiroStoryModel` is registered as the `miro` format but has no `render`/`parse` (`stories/stories.py:54`).
- Two example toolsets in `tools/sub_agent/fixtures.py` are installed as real toolsets (the installer skips `fixtures/` folders, not files).
- `cdd_guidance/patterns/source_text.py` duplicates `SourceText` in `clean_engineering/model/operation_metrics.py`.

## Progress (updated 2026-11-07, branch and main at 4c6ebb8d)

Every pass below ran the quick suite (3,328 examples at the last pass, no failures) and the 40 story tests before it was pushed. The heavy specs run once, together, at the end (rule `cdd_guidance/rules/test-timing.md`); the last full heavy run, on the guidance merge, passed.

| Area | Status |
|---|---|
| D — the 19 classes with no use | Done. Deleted, or kept with the use the review missed (design_canvas classes and `LernCanvasFixtures` are used by the UX canvas guidance; `OutputFolder` by the channel features; `MiroStoryModel` finished instead of removed) |
| Option A — one graph and one practice object per session | Done. `GraphPractice`, `GraphPractices`, `PracticeGraph` deleted; `node.practice`, `node.fidelity`, `node.rules`; explicit `graph.refresh(paths)` |
| Package moves | Done. health → diagnostics, installer → installation (mcp and hooks register with it), name → annotations, chat → harness, sub_agent and the toolsets → `tools` as one module, file_manager → space/session |
| harness core (annotations, process, markdown, agent_tools) | Done |
| installation, hooks, mcp | Done |
| harness upper (diagnostics, catalog, design_canvas, chat) | Done |
| guidance, guidance_actions | Done; each fidelity answers for its own text, `fidelity.actions` |
| space/repo, tools | Done |
| space/session | Done |
| actions, patterns, context setup, builders | Done |
| Practices round 1 (formats on one domain model) | Done |
| Practices round 2: Clean Engineering + BDD, DDD + agent BDD + overlays | Done |
| Practices round 2: Stories + UX | Done |
| DDD draw.io on Clean Engineering's diagram classes | Done; about 850 lines of DDD layout code deleted |
| space/kanban | Agent running, on top of the chat-defects branch |
| Follow-up fixes (recipes read their held fidelity, one format lookup, sketch lenses held, toolset probes, clean-ups) | Agent running |

What each agent skipped, and why, is in `.sessions/ensure-domain-orientation-refactor/pending-skipped-reshaping.md`; everything there is either assigned to a running agent or listed below.

**Still open after the running agents:** the old `_skip_inactive_fidelity` and `_activate(stage=...)` hooks in `ddd.py` and `stories.py`; the format as a `Format` object (read as a string by practices and the board); one Clean Engineering companion per session (needs a design). **Last:** the heavy specs in one batch, reinstall and catalog regeneration, a final validation round, and the closing report.

**Round 5 (cross-file validation, 2026-11-08):** see [round5-report.md](round5-report.md): 170 findings, 21 high. Nothing fixed yet.
- [Trend across rounds 1–5](trend-rounds-1-5.md): findings and severity per round.
