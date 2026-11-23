# Graph rule validation

**Generated:** 2026-11-19 18:55:05 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-scenarios-20261119T185426\graph.json`

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

**Total graph violations:** 66
**Rules with graph hits:** 3
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

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L198): Then `then the registered app of that name opens, Files or Story UI, whatever the case of its letters or the spaces around it`: Long Then 'the registered app of that name opens, Files or Story UI, whatever the case of its letters or the spaces around it' should name the next story on the map when continuing a flow.

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

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L68): When `when the Person presses the server health mark`: When step 'the Person presses the server health mark' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L165): When `when the Person presses the Kanban app on the server health panel`: When step 'the Person presses the Kanban app on the server health panel' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L172): When `when the Person presses the Kanban app on the server health panel`: When step 'the Person presses the Kanban app on the server health panel' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L204): When `when the Person presses the Graph app on the server health panel`: When step 'the Person presses the Graph app on the server health panel' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L211): When `when the Person presses the Graph app on the server health panel`: When step 'the Person presses the Graph app on the server health panel' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L219): When `when the Person presses the Graph app on the server health panel`: When step 'the Person presses the Graph app on the server health panel' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L225): When `when the Person presses the Graph app on the server health panel`: When step 'the Person presses the Graph app on the server health panel' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L232): When `when the Person presses the Graph app on the server health panel`: When step 'the Person presses the Graph app on the server health panel' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L238): When `when the Person presses the Kanban app on the server health panel`: When step 'the Person presses the Kanban app on the server health panel' names a UI gesture; state the domain intent instead.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L244): When `when the Person presses the Graph app on the server health panel`: When step 'the Person presses the Graph app on the server health panel' names a UI gesture; state the domain intent instead.

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

**Graph violations:** 55

- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L30): Then `then a green ✓ sits left of checkout-flow`: Then 'then a green ✓ sits left of checkout-flow' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L36): Then `then a red ✕ sits left of checkout-flow`: Then 'then a red ✕ sits left of checkout-flow' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L43): Then `then an amber ! sits left of checkout-flow`: Then 'then an amber ! sits left of checkout-flow' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L60): Then `then the session card opens with the panel on top, MCP host, Tools, Kanban app and Graph app green`: Then 'then the session card opens with the panel on top, MCP host, Tools, Kanban app and Graph app green' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L61): Then `and Tools reads 116 loaded, Kanban app 8778 and Graph app 5173`: Then 'and Tools reads 116 loaded, Kanban app 8778 and Graph app 5173' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L62): Then `and no Hook server part shows`: Then 'and no Hook server part shows' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L63): Then `and each part's name shows on hover`: Then 'and each part's name shows on hover' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L69): Then `then the session card and its panel stay open after the pointer leaves the mark`: Then 'then the session card and its panel stay open after the pointer leaves the mark' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L75): Then `then the headline reads Disconnected, plugin:cdd:cdd stopped.`: Then 'then the headline reads Disconnected, plugin:cdd:cdd stopped.' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L76): Then `and Details, Run install and Reconnect are offered`: Then 'and Details, Run install and Reconnect are offered' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L92): Then `then the mark shows ⟳ and the headline reads Reconnecting, Try 1 of 3.`: Then 'then the mark shows ⟳ and the headline reads Reconnecting, Try 1 of 3.' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L93): Then `and once cdd answers, the mark shows ✓ and the Chat Bar shows checkout-flow again, as in Display Stage Strip`: Then 'and once cdd answers, the mark shows ✓ and the Chat Bar shows checkout-flow again, as in Display Stage Strip' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L99): Then `then after Try 3 of 3 the headline reads Disconnected again`: Then 'then after Try 3 of 3 the headline reads Disconnected again' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L100): Then `and Reconnect and Run install are still offered`: Then 'and Reconnect and Run install are still offered' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L117): Then `then the panel says Installed. Open a new session to pick it up.`: Then 'then the panel says Installed. Open a new session to pick it up.' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L118): Then `and the installer that ran is scripts/install.py --ide Claude`: Then 'and the installer that ran is scripts/install.py --ide Claude' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L124): Then `then the panel says Install failed. See the error in Details.`: Then 'then the panel says Install failed. See the error in Details.' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L126): Then `then Details shows the tool server-health.report, the installer's error, the server plugin:cdd:cdd and the fix Press Reconnect. If that fails, press Run install.`: Then 'then Details shows the tool server-health.report, the installer's error, the server plugin:cdd:cdd and the fix Press Reconnect. If that fails, press Run install.' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L143): Then `then shop is a repository on main`: Then 'then shop is a repository on main' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L144): Then `and its first commit holds .gitignore, README.md and notes.md`: Then 'and its first commit holds .gitignore, README.md and notes.md' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L145): Then `and .claude and the session's log are ignored`: Then 'and .claude and the session's log are ignored' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L151): Then `then its first commit holds each of those files`: Then 'then its first commit holds each of those files' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L152): Then `and its .gitignore lists only what CDD writes into a project`: Then 'and its .gitignore lists only what CDD writes into a project' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L166): Then `then the board page for this repository opens in the browser pane`: Then 'then the board page for this repository opens in the browser pane' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L167): Then `and nothing was started`: Then 'and nothing was started' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L173): Then `then the board server starts from the repository's own folder`: Then 'then the board server starts from the repository's own folder' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L174): Then `and once it answers, the board page opens in the browser pane`: Then 'and once it answers, the board page opens in the browser pane' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L182): Then `then the Files page's link names the worktree C:\dev\abd-cdd-file-manager as its project, not the main checkout C:\dev\abd-context-driven-delivery`: Then 'then the Files page's link names the worktree C:\dev\abd-cdd-file-manager as its project, not the main checkout C:\dev\abd-context-driven-delivery' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L183): Then `and every call the page makes is answered by the dev lane's server, on the ticket's code`: Then 'and every call the page makes is answered by the dev lane's server, on the ticket's code' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L189): Then `then the Files page's link names the main checkout as its project`: Then 'then the Files page's link names the main checkout as its project' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L190): Then `and every call the page makes is answered by the stable lane's server`: Then 'and every call the page makes is answered by the stable lane's server' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L198): Then `then the registered app of that name opens, Files or Story UI, whatever the case of its letters or the spaces around it`: Then 'then the registered app of that name opens, Files or Story UI, whatever the case of its letters or the spaces around it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L199): Then `and a name no app is registered as, such as "Nowhere", is still refused, naming the apps there are`: Then 'and a name no app is registered as, such as "Nowhere", is still refused, naming the apps there are' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L205): Then `then the Graph app opens in the browser pane, and no start script runs`: Then 'then the Graph app opens in the browser pane, and no start script runs' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L206): Then `and the browser pane is shown beside the chat`: Then 'and the browser pane is shown beside the chat' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L212): Then `then its web server and its app start, with the repository's Python, in that order`: Then 'then its web server and its app start, with the repository's Python, in that order' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L213): Then `and the Graph app opens where its start script says it answers`: Then 'and the Graph app opens where its start script says it answers' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L214): Then `and the Person is told it is starting`: Then 'and the Person is told it is starting' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L220): Then `then nothing opens, and the Person is told which script failed and where its log is`: Then 'then nothing opens, and the Person is told which script failed and where its log is' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L226): Then `then nothing opens anywhere else`: Then 'then nothing opens anywhere else' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L227): Then `and the Person is told where the app is and why it did not open`: Then 'and the Person is told where the app is and why it did not open' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L233): Then `then the Person is told the page did not load, in the pane's own words`: Then 'then the Person is told the page did not load, in the pane's own words' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L239): Then `then the board page opens with the chat's ticket selected`: Then 'then the board page opens with the chat's ticket selected' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/move-work-forward-from-chat-bar/check-cdd-server-health-in-chat-bar/check_cdd_server_health_in_chat_bar_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\move-work-forward-from-chat-bar\check-cdd-server-health-in-chat-bar\check_cdd_server_health_in_chat_bar_story.test.md#L245): Then `then the Graph app opens on the session's path`: Then 'then the Graph app opens on the session's path' has no observes relationship to Example, which the stories practice schema requires.
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
