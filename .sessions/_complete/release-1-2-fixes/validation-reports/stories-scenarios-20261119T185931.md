# Graph rule validation

**Generated:** 2026-11-19 19:00:14 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-scenarios-20261119T185931\graph.json`

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

**Total graph violations:** 22
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

**Graph violations:** 22

- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/check-artifacts-against-rules/check_artifacts_against_rules_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\check-artifacts-against-rules\check_artifacts_against_rules_story.test.md#L55): Then `then the report hands the judge ++verb-noun-format++`: Then 'then the report hands the judge ++verb-noun-format++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/check-artifacts-against-rules/check_artifacts_against_rules_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\check-artifacts-against-rules\check_artifacts_against_rules_story.test.md#L56): Then `and the report leaves ++child-count-fits-layer++ out`: Then 'and the report leaves ++child-count-fits-layer++ out' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/check-artifacts-against-rules/check_artifacts_against_rules_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\check-artifacts-against-rules\check_artifacts_against_rules_story.test.md#L64): Then `then the call is refused, saying there is no rule ++no-such-rule++`: Then 'then the call is refused, saying there is no rule ++no-such-rule++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/check-artifacts-against-rules/check_artifacts_against_rules_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\check-artifacts-against-rules\check_artifacts_against_rules_story.test.md#L65): Then `and the refusal lists ++verb-noun-format++ among the rules there are`: Then 'and the refusal lists ++verb-noun-format++ among the rules there are' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/check-artifacts-against-rules/check_artifacts_against_rules_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\check-artifacts-against-rules\check_artifacts_against_rules_story.test.md#L74): Then `then the report holds the limit-operation-parameters violation in ++src/orders/order.ts++`: Then 'then the report holds the limit-operation-parameters violation in ++src/orders/order.ts++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/check-artifacts-against-rules/check_artifacts_against_rules_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\check-artifacts-against-rules\check_artifacts_against_rules_story.test.md#L82): Then `then the call is refused, naming ++no/such/graph.json++ as not there, read from the project's root`: Then 'then the call is refused, naming ++no/such/graph.json++ as not there, read from the project's root' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L63): Then `then the call is refused, saying no practice or fidelity has the slug ++stories_story_map++`: Then 'then the call is refused, saying no practice or fidelity has the slug ++stories_story_map++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L64): Then `and the refusal lists ++stories-story-map++ among the slugs there are`: Then 'and the refusal lists ++stories-story-map++ among the slugs there are' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L72): Then `then the answer holds ++write the story map++`: Then 'then the answer holds ++write the story map++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L80): Then `then the answer holds the rules of ++stories-story-map++`: Then 'then the answer holds the rules of ++stories-story-map++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L88): Then `then ++{foo: bar}++ is refused, saying a mapping names its practice in toolset`: Then 'then ++{foo: bar}++ is refused, saying a mapping names its practice in toolset' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L89): Then `and the refusal lists ++stories-story-map++ among the slugs there are`: Then 'and the refusal lists ++stories-story-map++ among the slugs there are' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L108): Then `then the saved file is .context/returns.drawio, which draws Return Damaged Book`: Then 'then the saved file is .context/returns.drawio, which draws Return Damaged Book' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L109): Then `and ++.context/story-map.drawio++ is as the person left it`: Then 'and ++.context/story-map.drawio++ is as the person left it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L118): Then `then the call is refused, naming ++.context/empty.md++ as empty`: Then 'then the call is refused, naming ++.context/empty.md++ as empty' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L119): Then `and ++.context/story-map.drawio++ is as it was`: Then 'and ++.context/story-map.drawio++ is as it was' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L127): Then `then ++../outside/story-map.md++ is refused as not under the session's root`: Then 'then ++../outside/story-map.md++ is refused as not under the session's root' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L128): Then `and no drawing is saved beside ++../outside/story-map.md++`: Then 'and no drawing is saved beside ++../outside/story-map.md++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/produce_formal_artifacts_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\produce_formal_artifacts_story.test.md#L136): Then `then the saved file is ++.context/story-map.drawio++, which draws Place Order`: Then 'then the saved file is ++.context/story-map.drawio++, which draws Place Order' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/turn-source-material-into-context/turn_source_material_into_context_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\turn-source-material-into-context\turn_source_material_into_context_story.test.md#L46): Then `then the instructions name ++.context/story-map.md++ as the path to scan`: Then 'then the instructions name ++.context/story-map.md++ as the path to scan' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/turn-source-material-into-context/turn_source_material_into_context_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\turn-source-material-into-context\turn_source_material_into_context_story.test.md#L54): Then `then the call is refused, naming ++nope/missing.md++ as not there`: Then 'then the call is refused, naming ++nope/missing.md++ as not there' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/turn-source-material-into-context/turn_source_material_into_context_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\turn-source-material-into-context\turn_source_material_into_context_story.test.md#L62): Then `then ++../outside/story-map.md++ is refused as not under the session's root`: Then 'then ++../outside/story-map.md++ is refused as not under the session's root' has no observes relationship to Example, which the stories practice schema requires.
