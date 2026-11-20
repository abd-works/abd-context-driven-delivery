# Graph rule validation

**Generated:** 2026-11-20 19:01:50 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\clean-engineering-code-20261120T190010\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
- `.context`
- `cdd_guidance`
- `cdd_guidance/actions`
- `cdd_guidance/builders`
- `cdd_guidance/catalog`
- `cdd_guidance/context_setup`
- `cdd_guidance/patterns`
- `cdd_guidance/practices`
- `harness`
- `harness/agent_tools`
- `harness/annotations`
- `harness/catalog_generator`
- `harness/chat`
- `harness/chat-ui`
- `harness/design_canvas`
- `harness/diagnostics`
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
- `harness/whiteboard`
- `scripts`
- `scripts/unit_guard`
- `space`
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
- `story_tests/review-generated-work-in-file-viewer`
- `tools`
- `tools/drawio_viewer`
- `tools/echo`
- `tools/error_display`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/prompt_queue`
- `tools/sub_agent`

## Summary

**Total graph violations:** 1
**Rules with graph hits:** 1
**AI rules in scope:** 24

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-source`

Rule text: [clean_engineering/clean_engineering.md:18](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L18)

### `do-not-invent-terms`

Rule text: [clean_engineering/clean_engineering.md:19](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L19)

### `do-not-invent-parallel-object-models`

Rule text: [clean_engineering/clean_engineering.md:20](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L20)

### `hide-inner-details`

Rule text: [clean_engineering/clean_engineering.md:233](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L233)

### `hold-state-on-the-object-not-in-parameters`

Rule text: [clean_engineering/clean_engineering.md:243](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L243)

### `keep-operations-small-focused`

Rule text: [clean_engineering/clean_engineering.md:325](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L325)

### `prefer-instance-operations`

Rule text: [clean_engineering/clean_engineering.md:326](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L326)

### `keep-operations-single-responsibility`

Rule text: [clean_engineering/clean_engineering.md:241](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L241)

### `simplify-control-flow`

Rule text: [clean_engineering/clean_engineering.md:328](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L328)

### `errors-out-of-existence`

Rule text: [clean_engineering/clean_engineering.md:245](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L245)

### `no-prototype-swapping`

Rule text: [clean_engineering/clean_engineering.md:330](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L330)

### `use-intention-revealing-names`

Rule text: [clean_engineering/clean_engineering.md:258](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L258)

### `use-consistent-naming`

Rule text: [clean_engineering/clean_engineering.md:259](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L259)

### `provide-meaningful-context`

Rule text: [clean_engineering/clean_engineering.md:335](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L335)

### `eliminate-duplication`

Rule text: [clean_engineering/clean_engineering.md:260](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L260)

### `no-legacy-api-after-refactor`

Rule text: [clean_engineering/clean_engineering.md:337](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L337)

### `use-exceptions-properly`

Rule text: [clean_engineering/clean_engineering.md:340](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L340)

### `never-swallow-exceptions`

Rule text: [clean_engineering/clean_engineering.md:341](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L341)

### `limit-comments`

Rule text: [clean_engineering/clean_engineering.md:248](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L248)

### `source-parses`

Rule text: [clean_engineering/clean_engineering.md:343](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L343)

### `operation-has-a-proving-test`

Rule text: [tdd/tdd.md:162](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L162)

### `class-demonstrated-by-a-test`

Rule text: [tdd/tdd.md:163](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L163)

### `invariant-has-a-failing-case`

Rule text: [tdd/tdd.md:164](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L164)

### `every-branch-taken-by-a-test`

Rule text: [tdd/tdd.md:165](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\tdd\tdd.md#L165)

### `use-explicit-dependencies`

Rule text: [clean_engineering/clean_engineering.md:236](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L236)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/bdd/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\bdd\model\graph_reading.py#L106): OoadClass `ObservationLinks`: Class 'ObservationLinks' constructs 'ImportedClasses' inside its constructor.
