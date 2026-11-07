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
