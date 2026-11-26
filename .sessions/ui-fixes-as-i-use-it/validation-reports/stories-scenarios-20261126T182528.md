# Graph rule validation

**Generated:** 2026-11-26 18:30:02 UTC
**Project:** abd-cdd-ui-fixes-as-i-use-it
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-ui-fixes-as-i-use-it\.sessions\ui-fixes-as-i-use-it\.context\checked-graphs\stories-scenarios-20261126T182528\graph.json`

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

**Total graph violations:** 2
**Rules with graph hits:** 2
**Candidates for the judge to read:** 5. A rule that requires a judge listed each; none is a violation until the judge reads it and fails it.
**AI rules in scope:** 27

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6). A hit marked `**CANDIDATE**` comes from a rule that requires a judge: its check only lists places to read, so read each and fail the rule only where the reading finds it broken.

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `gwt-steps-trace-to-domain-operations`

Rule text: [stories/stories.md:167](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L167)

### `behavioral-and-system-observable-outcomes`

Rule text: [stories/stories.md:168](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L168)

### `explore-full-interaction-surface`

Rule text: [stories/stories.md:169](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L169)

### `edge-and-error-cases-have-scenarios`

Rule text: [stories/stories.md:170](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L170)

### `examples-trace-domain-model`

Rule text: [stories/stories.md:171](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L171)

### `reconcile-live-immediately`

Rule text: [stories/stories.md:172](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L172)

### `flagged-writes-intended-gwt`

Rule text: [stories/stories.md:173](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L173)

### `main-flow-first`

Rule text: [stories/stories.md:174](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L174)

### `scenarios-name-a-story-on-the-map`

Rule text: [stories/stories.md:175](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L175)

### `given-only-what-the-system-checks`

Rule text: [stories/stories.md:176](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L176)

### `given-names-complex-state-root-first`

Rule text: [stories/stories.md:177](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L177)

### `but-marks-missing-state`

Rule text: [stories/stories.md:178](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L178)

### `when-holds-the-operation`

Rule text: [stories/stories.md:179](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L179)

### `when-names-intent-not-interface-gesture`

Rule text: [stories/stories.md:180](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L180)

**Candidates for the judge to read:** 5

- [?] **CANDIDATE** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\story_tests\review-generated-work-in-file-viewer\act-on-files-from-file-menu\act_on_files_from_file_menu_story.test.md#L24): When `when the Person right-clicks *notes.md* and chooses *Delete*`: When step 'the Person right-clicks *notes.md* and chooses *Delete*' names a UI gesture; state the domain intent instead.
- [?] **CANDIDATE** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\story_tests\review-generated-work-in-file-viewer\act-on-files-from-file-menu\act_on_files_from_file_menu_story.test.md#L63): When `when the Person right-clicks *story-map.md* and chooses *Validate*`: When step 'the Person right-clicks *story-map.md* and chooses *Validate*' names a UI gesture; state the domain intent instead.
- [?] **CANDIDATE** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\story_tests\review-generated-work-in-file-viewer\act-on-files-from-file-menu\act_on_files_from_file_menu_story.test.md#L84): When `when the Person right-clicks *story-map.md* and chooses *Display violations*`: When step 'the Person right-clicks *story-map.md* and chooses *Display violations*' names a UI gesture; state the domain intent instead.
- [?] **CANDIDATE** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\story_tests\review-generated-work-in-file-viewer\act-on-files-from-file-menu\act_on_files_from_file_menu_story.test.md#L86): When `when the Person presses the violation`: When step 'the Person presses the violation' names a UI gesture; state the domain intent instead.
- [?] **CANDIDATE** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\story_tests\review-generated-work-in-file-viewer\act-on-files-from-file-menu\act_on_files_from_file_menu_story.test.md#L106): When `when the Person right-clicks *story_tests/checkout* and points at *Add to practice*`: When step 'the Person right-clicks *story_tests/checkout* and points at *Add to practice*' names a UI gesture; state the domain intent instead.

### `expressive-system-interactions`

Rule text: [stories/stories.md:181](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L181)

### `and-chaining`

Rule text: [stories/stories.md:182](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L182)

### `outline-requires-many-permutations`

Rule text: [stories/stories.md:183](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L183)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\story_tests\review-generated-work-in-file-viewer\act-on-files-from-file-menu\act_on_files_from_file_menu_story.test.md#L42): Scenario `Refuse what may not be deleted`: Scenario outline 'Refuse what may not be deleted' needs more than two example rows (found 0).

### `plain-english-gwt-steps`

Rule text: [stories/stories.md:184](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L184)

### `seed-prior-story-as-given`

Rule text: [stories/stories.md:185](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L185)

### `domain-terms-link-to-model`

Rule text: [stories/stories.md:186](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L186)

### `then-observes-an-example`

Rule text: [stories/stories.md:187](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L187)

### `step-says-more-than-an-example-name`

Rule text: [stories/stories.md:188](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L188)

### `scenarios-differ-in-when-or-outcome`

Rule text: [stories/stories.md:189](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L189)

### `person-stories-show-the-person-acting`

Rule text: [stories/stories.md:190](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L190)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/act-on-files-from-file-menu/act_on_files_from_file_menu_story.test.md](C:\dev\abd-cdd-ui-fixes-as-i-use-it\story_tests\review-generated-work-in-file-viewer\act-on-files-from-file-menu\act_on_files_from_file_menu_story.test.md#L118): Scenario `Refuse a path outside the project`: Scenario 'Refuse a path outside the project' of the Person's story 'Add File Or Folder To Practice' has no When in which the Person acts ('a path outside the project is added to a practice'); merge it into a scenario the Person acts in, or move it to a system story.
