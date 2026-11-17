# Graph rule validation

**Generated:** 2026-11-17 04:44:26 UTC
**Project:** abd-cdd-simple-queue
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\simple-queue\.context\checked-graphs\clean-engineering-modules-20261117T044308\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.`
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
- `story_tests/deliver-work-with-context-guidance`
- `story_tests/move-work-forward-from-chat-bar`
- `story_tests/move-work-forward-on-session-board`
- `story_tests/register-and-install-toolsets`
- `story_tests/review-generated-work-in-file-viewer`
- `tools`
- `tools/drawio_viewer`
- `tools/echo`
- `tools/error_display`
- `tools/granola`
- `tools/prompt_log`
- `tools/prompt_notify`
- `tools/sub_agent`

## Summary

**Total graph violations:** 8
**Rules with graph hits:** 1
**AI rules in scope:** 21

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-source`

Rule text: [clean_engineering/clean_engineering.md:18](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L18)

### `do-not-invent-terms`

Rule text: [clean_engineering/clean_engineering.md:19](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L19)

### `do-not-invent-parallel-object-models`

Rule text: [clean_engineering/clean_engineering.md:20](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L20)

### `domain-nouns-only`

Rule text: [clean_engineering/clean_engineering.md:127](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L127)

### `named-seam-and-constraint`

Rule text: [clean_engineering/clean_engineering.md:128](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L128)

### `high-cohesion`

Rule text: [clean_engineering/clean_engineering.md:129](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L129)

### `no-module-per-class`

Rule text: [clean_engineering/clean_engineering.md:130](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L130)

### `single-boundary`

Rule text: [clean_engineering/clean_engineering.md:131](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L131)

### `deep-module`

Rule text: [clean_engineering/clean_engineering.md:135](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L135)

### `abstraction-focus`

Rule text: [clean_engineering/clean_engineering.md:136](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L136)

### `language-opens-the-card`

Rule text: [clean_engineering/clean_engineering.md:137](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L137)

### `purpose-before-mechanism`

Rule text: [clean_engineering/clean_engineering.md:138](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L138)

### `public-seam-only`

Rule text: [clean_engineering/clean_engineering.md:139](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L139)

### `use-typed-signatures`

Rule text: [clean_engineering/clean_engineering.md:140](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L140)

### `general-purpose-surface`

Rule text: [clean_engineering/clean_engineering.md:141](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L141)

### `temporal-independence`

Rule text: [clean_engineering/clean_engineering.md:142](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L142)

### `seam-names-current-code`

Rule text: [clean_engineering/clean_engineering.md:143](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L143)

### `one-way-deps`

Rule text: [clean_engineering/clean_engineering.md:147](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L147)

### `extensions-live-with-the-domain`

Rule text: [clean_engineering/clean_engineering.md:148](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L148)

### `low-coupling`

Rule text: [clean_engineering/clean_engineering.md:149](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L149)

### `layer-separation`

Rule text: [clean_engineering/clean_engineering.md:150](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L150)

### `use-intention-revealing-names`

Rule text: [clean_engineering/clean_engineering.md:258](C:\Users\jeffa\.cdd\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L258)

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/icon-button-view.tsx](C:\dev\abd-cdd-simple-queue\tools\prompt_queue\hooks\queue\icon-button-view.tsx#L59): Parameter `x`: Parameter 'x' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-simple-queue\tools\prompt_queue\hooks\queue\prompt-queue.ts#L78): Parameter `to`: Parameter 'to' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/prompt-queue.ts](C:\dev\abd-cdd-simple-queue\tools\prompt_queue\hooks\queue\prompt-queue.ts#L83): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-order.ts](C:\dev\abd-cdd-simple-queue\tools\prompt_queue\hooks\queue\queue-order.ts#L27): Parameter `to`: Parameter 'to' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-order.ts](C:\dev\abd-cdd-simple-queue\tools\prompt_queue\hooks\queue\queue-order.ts#L39): Parameter `id`: Parameter 'id' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-simple-queue\tools\prompt_queue\hooks\queue\queue-view.tsx#L49): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-simple-queue\tools\prompt_queue\hooks\queue\queue-view.tsx#L103): Parameter `e`: Parameter 'e' does not reveal intent.
- [X] **ERROR** **[graph rule]** - [tools/prompt_queue/hooks/queue/queue-view.tsx](C:\dev\abd-cdd-simple-queue\tools\prompt_queue\hooks\queue\queue-view.tsx#L141): Parameter `e`: Parameter 'e' does not reveal intent.
