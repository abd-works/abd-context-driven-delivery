# Graph rule validation

**Generated:** 2026-11-27 17:06:08 UTC
**Project:** abd-cdd-ui-fixes-as-i-use-it
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-ui-fixes-as-i-use-it\.sessions\ui-fixes-as-i-use-it\.context\checked-graphs\stories-hardening-20261127T170604\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `.context`
- `cdd_guidance`
- `cdd_guidance/actions`
- `cdd_guidance/align`
- `cdd_guidance/builders`
- `cdd_guidance/catalog`
- `cdd_guidance/context_setup`
- `cdd_guidance/diagnostics`
- `cdd_guidance/patterns`
- `cdd_guidance/practices`
- `harness`
- `harness/agent_tools`
- `harness/annotations`
- `harness/apps`
- `harness/catalog_generator`
- `harness/chat`
- `harness/chat-ui`
- `harness/design_canvas`
- `harness/diagnostics`
- `harness/drawio`
- `harness/e2e_review`
- `harness/files_app`
- `harness/git`
- `harness/graph`
- `harness/guidance`
- `harness/guidance_actions`
- `harness/hooks`
- `harness/installation`
- `harness/markdown`
- `harness/mcp`
- `harness/process`
- `harness/release`
- `harness/whiteboard`
- `scripts`
- `scripts/names_exist`
- `scripts/unit_guard`
- `space`
- `space/.context`
- `space/kanban`
- `space/repo`
- `space/session`
- `story_tests`
- `story_tests/author-story-maps`
- `story_tests/build-design-canvas-screens`
- `story_tests/connect-sessions-across-channels-and-apps`
- `story_tests/deliver-work-with-context-guidance`
- `story_tests/draw-practice-models-on-claude-whiteboard`
- `story_tests/explore-stories-in-story-ui`
- `story_tests/map-work-into-knowledge-graph`
- `story_tests/move-work-forward-from-chat-bar`
- `story_tests/move-work-forward-on-session-board`
- `story_tests/queue-prompts-for-later`
- `story_tests/register-and-install-toolsets`
- `story_tests/review-end-to-end-screens`
- `story_tests/review-generated-work-in-file-viewer`
- `tools`
- `tools/.context`
- `tools/drawio_viewer`
- `tools/echo`
- `tools/error_display`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/prompt_queue`
- `tools/sub_agent`

## Summary

**No graph rule ran on:** `.sessions/ui-fixes-as-i-use-it/exploratory-testing`. The graph read no node from them, so only the AI rules judge them.
**AI rules in scope:** 14

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6). A hit marked `**CANDIDATE**` comes from a rule that requires a judge: its check only lists places to read, so read each and fail the rule only where the reading finds it broken.

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `themes-confirmed-by-the-person`

Rule text: [tdd/tdd.md:256](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L256)

### `scope-is-what-the-release-changed`

Rule text: [tdd/tdd.md:257](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L257)

### `one-robot-per-theme`

Rule text: [tdd/tdd.md:258](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L258)

### `every-theme-has-a-robot-report`

Rule text: [tdd/tdd.md:259](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L259)

### `defects-reported-as-found`

Rule text: [tdd/tdd.md:260](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L260)

### `defects-fixed-by-a-robot-per-code-area`

Rule text: [tdd/tdd.md:261](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L261)

### `every-defect-triaged`

Rule text: [tdd/tdd.md:262](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L262)

### `one-commit-per-defect-fix`

Rule text: [tdd/tdd.md:263](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L263)

### `regression-after-exploratory-testing`

Rule text: [tdd/tdd.md:266](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L266)

### `every-story-run-at-e2e`

Rule text: [tdd/tdd.md:267](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L267)

### `every-story-judged-against-the-last-release`

Rule text: [tdd/tdd.md:268](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L268)

## Judgment — `.sessions/ui-fixes-as-i-use-it/exploratory-testing/final-report.md`

### `every-story-run-at-e2e` — Fail
- final-report.md:91 The queue plugin e2e spec was not verified (the headless Claude Code chat's subscription is refused), so the queue band's stories have no e2e run on the release's commit.
- final-report.md:92 The agentic BDD specs were not run (`-SkipAgents`), so the stories they hold have no e2e run.
- final-report.md:115 Five board sub-epics and every Python browser spec record no step screens: their assertions ran at e2e, but no screen of theirs was captured to check.

### `every-story-judged-against-the-last-release` — Fail
- final-report.md:107 No sub-epic has an accepted run for v1.2.1 or any release before it, so no screen was compared with the last release, and `changed_pairs` lists nothing to judge.
- final-report.md:117 The person has not yet accepted the three recorded runs, so the release is not ready under `person-accepts-the-baseline`.

### `defects-fixed-by-a-robot-per-code-area` — Fail
- final-report.md:18 The defects the regression run found (bolt-2, bolt-4, bolt-5) were fixed by the supervisor Bolt, not by the fixing robot that owns the code area (`harness/files_app`, `harness/graph`, `harness/e2e_review`).

## Judgment — `.sessions/ui-fixes-as-i-use-it/exploratory-testing/defects/bolt-2-format-press-dropped-while-list-read-again.md`

### `every-defect-triaged` — Fail
- bolt-2-format-press-dropped-while-list-read-again.md:20 Triaged by Bolt, who reported it; triage must be by someone other than the reporter.

## Judgment — `.sessions/ui-fixes-as-i-use-it/exploratory-testing/defects/bolt-4-property-named-properties-is-its-own-parent.md`

### `every-defect-triaged` — Fail
- bolt-4-property-named-properties-is-its-own-parent.md:20 Triaged by Bolt, who reported it.

## Judgment — `.sessions/ui-fixes-as-i-use-it/exploratory-testing/defects/bolt-5-e2e-review-refused-on-pinned-runtime.md`

### `every-defect-triaged` — Fail
- bolt-5-e2e-review-refused-on-pinned-runtime.md:19 Triaged by Bolt, who reported it.

## Judgment — `.sessions/ui-fixes-as-i-use-it/exploratory-testing/defects/gizmo-1-delete-through-junction-deletes-target-folder.md`

### `one-commit-per-defect-fix` — Fail
- gizmo-1-delete-through-junction-deletes-target-folder.md:50 Commit d64447e5d holds the fixes of gizmo-1, 2, 3, 6 and 8 and halves of gizmo-4 and 5, so none of them can be reverted or traced alone.

## Judgment — `.sessions/ui-fixes-as-i-use-it/exploratory-testing/defects/widget-1-domain-model-roundtrip-moves-language-to-kept.md`

### `one-commit-per-defect-fix` — Fail
- widget-1-domain-model-roundtrip-moves-language-to-kept.md:50 Commit dfe41aa2a holds widget-1, widget-5 and widget-8. The defect file says one reader change fixed all three, but the rule asks for a commit per defect, and their tests could have landed one at a time.

## Passes

| Rule | Evidence |
|---|---|
| `vocabulary-traces-to-domain-source` | Reports and defects use the code's own names (format chips, roots, robot rows, `send_to_chat`, `ReportTool`). |
| `read-all-source-context-in-full` | Each defect file names its module, class and the commit behind it; themes name the changes behind them. |
| `do-not-invent-requirements` | Behaviour questions (pip-3, bolt-3, rivet-7, widget-2, gizmo-5/6/9) are left to the person, not decided. |
| `themes-confirmed-by-the-person` | coverage-themes.md:3, the seven areas the person named on card 7651c123c132; none added. |
| `scope-is-what-the-release-changed` | Each theme names its commits on the branch (coverage-themes.md:21 and siblings). |
| `one-robot-per-theme` | Four charters, four robots (Pip, Rivet, Gizmo, Widget), each with its own sandbox, `CDD_HOME` and ports (charters.md:17, 25). |
| `every-theme-has-a-robot-report` | report-pip.md, report-rivet.md, report-gizmo.md, report-widget.md. |
| `defects-reported-as-found` | 41 defect files, each with a `[defect]` card on chat 82179ef0's queue. |
| `regression-after-exploratory-testing` | final-report.md:81, run after every exploratory fix was committed; tiers rerun after the regression's own fixes. |
