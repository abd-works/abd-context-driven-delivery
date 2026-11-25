# Graph rule validation

**Generated:** 2026-11-19 18:49:47 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-scenarios-20261119T184909\graph.json`

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

**Total graph violations:** 11
**Rules with graph hits:** 1
**AI rules in scope:** 21

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `gwt-steps-trace-to-domain-operations`

Rule text: [stories/stories.md:142](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L142)

### `behavioral-and-system-observable-outcomes`

Rule text: [stories/stories.md:143](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L143)

### `explore-full-interaction-surface`

Rule text: [stories/stories.md:144](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L144)

### `examples-trace-domain-model`

Rule text: [stories/stories.md:145](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L145)

### `reconcile-live-immediately`

Rule text: [stories/stories.md:146](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L146)

### `flagged-writes-intended-gwt`

Rule text: [stories/stories.md:147](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L147)

### `scenario-names-continuation`

Rule text: [stories/stories.md:148](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L148)

### `given-only-what-the-system-checks`

Rule text: [stories/stories.md:149](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L149)

### `given-names-complex-state-root-first`

Rule text: [stories/stories.md:150](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L150)

### `but-marks-missing-state`

Rule text: [stories/stories.md:151](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L151)

### `when-holds-the-operation`

Rule text: [stories/stories.md:152](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L152)

### `when-names-intent-not-interface-gesture`

Rule text: [stories/stories.md:153](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L153)

### `expressive-system-interactions`

Rule text: [stories/stories.md:154](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L154)

### `and-chaining`

Rule text: [stories/stories.md:155](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L155)

### `outline-requires-many-permutations`

Rule text: [stories/stories.md:156](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L156)

### `plain-english-gwt-steps`

Rule text: [stories/stories.md:157](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L157)

### `seed-prior-story-as-given`

Rule text: [stories/stories.md:158](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L158)

### `domain-terms-link-to-model`

Rule text: [stories/stories.md:159](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L159)

### `conforms-to-schema`

Rule text: a graph rule, written in no practice document

**Graph violations:** 11

- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L32): Then `then the files the install wrote into shop/.cursor are removed`: Then 'then the files the install wrote into shop/.cursor are removed' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L33): Then `and the install in shop/.claude is left as it is`: Then 'and the install in shop/.claude is left as it is' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L39): Then `then the record in C:/work/shop/.claude names the folder C:/work/shop/.claude`: Then 'then the record in C:/work/shop/.claude names the folder C:/work/shop/.claude' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L40): Then `and a clean run from any other directory removes the files that install wrote`: Then 'and a clean run from any other directory removes the files that install wrote' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L46): Then `then the record in shop/.cursor lists the generate skill`: Then 'then the record in shop/.cursor lists the generate skill' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L47): Then `and a clean of shop/.cursor removes it`: Then 'and a clean of shop/.cursor removes it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L53): Then `then the second waits for the first`: Then 'then the second waits for the first' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L54): Then `and both finish`: Then 'and both finish' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L55): Then `and every file the record lists is in shop/.cursor`: Then 'and every file the record lists is in shop/.cursor' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L61): Then `then the second is refused, naming shop/.claude and process 4812`: Then 'then the second is refused, naming shop/.claude and process 4812' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/register-and-install-toolsets/install-markdown-files/install_markdown_files_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\register-and-install-toolsets\install-markdown-files\install_markdown_files_story.test.md#L67): Then `then the install runs`: Then 'then the install runs' has no observes relationship to Example, which the stories practice schema requires.
