# Graph rule validation

**Generated:** 2026-11-17 17:34:48 UTC
**Project:** abd-cdd-simple-queue-enhancement
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\simple-queue-enhancements\.context\checked-graphs\stories-scenarios-20261117T173330\graph.json`

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
**Rules with graph hits:** 7
**AI rules in scope:** 42

## Rules

Each rule names where its text is kept, then any graph scanner hits (`**[graph rule]**`). The judgment is appended after the rules, in the shape the Validate action gives (`cdd_guidance/actions/validate/validate.md`, step 6).

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `gwt-steps-trace-to-domain-operations`

Rule text: [stories/stories.md:140](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L140)

### `behavioral-and-system-observable-outcomes`

Rule text: [stories/stories.md:141](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L141)

### `explore-full-interaction-surface`

Rule text: [stories/stories.md:142](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L142)

### `examples-trace-domain-model`

Rule text: [stories/stories.md:143](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L143)

### `reconcile-live-immediately`

Rule text: [stories/stories.md:144](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L144)

### `flagged-writes-intended-gwt`

Rule text: [stories/stories.md:145](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L145)

### `scenario-names-continuation`

Rule text: [stories/stories.md:146](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L146)

### `given-only-what-the-system-checks`

Rule text: [stories/stories.md:147](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L147)

### `given-names-complex-state-root-first`

Rule text: [stories/stories.md:148](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L148)

### `but-marks-missing-state`

Rule text: [stories/stories.md:149](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L149)

### `when-holds-the-operation`

Rule text: [stories/stories.md:150](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L150)

### `when-names-intent-not-interface-gesture`

Rule text: [stories/stories.md:151](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L151)

### `expressive-system-interactions`

Rule text: [stories/stories.md:152](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L152)

### `and-chaining`

Rule text: [stories/stories.md:153](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L153)

### `outline-requires-many-permutations`

Rule text: [stories/stories.md:154](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L154)

### `plain-english-gwt-steps`

Rule text: [stories/stories.md:155](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L155)

### `seed-prior-story-as-given`

Rule text: [stories/stories.md:156](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L156)

### `domain-terms-link-to-model`

Rule text: [stories/stories.md:157](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L157)

### `vocabulary-traces-to-domain-source`

Rule text: [stories/stories.md:24](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L24)

### `read-all-source-context-in-full`

Rule text: [stories/stories.md:25](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L25)

### `do-not-invent-requirements`

Rule text: [stories/stories.md:26](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L26)

### `gwt-steps-trace-to-domain-operations`

Rule text: [stories/stories.md:140](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L140)

### `behavioral-and-system-observable-outcomes`

Rule text: [stories/stories.md:141](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L141)

### `explore-full-interaction-surface`

Rule text: [stories/stories.md:142](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L142)

### `examples-trace-domain-model`

Rule text: [stories/stories.md:143](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L143)

### `reconcile-live-immediately`

Rule text: [stories/stories.md:144](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L144)

### `flagged-writes-intended-gwt`

Rule text: [stories/stories.md:145](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L145)

### `scenario-names-continuation`

Rule text: [stories/stories.md:146](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L146)

### `given-only-what-the-system-checks`

Rule text: [stories/stories.md:147](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L147)

### `given-names-complex-state-root-first`

Rule text: [stories/stories.md:148](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L148)

### `but-marks-missing-state`

Rule text: [stories/stories.md:149](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L149)

### `when-holds-the-operation`

Rule text: [stories/stories.md:150](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L150)

### `when-names-intent-not-interface-gesture`

Rule text: [stories/stories.md:151](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L151)

### `expressive-system-interactions`

Rule text: [stories/stories.md:152](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L152)

### `and-chaining`

Rule text: [stories/stories.md:153](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L153)

### `outline-requires-many-permutations`

Rule text: [stories/stories.md:154](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L154)

### `plain-english-gwt-steps`

Rule text: [stories/stories.md:155](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L155)

### `seed-prior-story-as-given`

Rule text: [stories/stories.md:156](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L156)

### `domain-terms-link-to-model`

Rule text: [stories/stories.md:157](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L157)

### `behaviours-not-one-time-tasks`

Rule text: [stories/stories.md:86](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L86)

**Graph violations:** 4

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L499): Story `Check Ticket Branches Once Per Board Build`: Story 'Check Ticket Branches Once Per Board Build' reads like a one-time task, not a repeatable behaviour.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L507): Story `Read Session File Once Per Board Build`: Story 'Read Session File Once Per Board Build' reads like a one-time task, not a repeatable behaviour.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1621): Story `Store Each Screenshot Once By Content Hash`: Story 'Store Each Screenshot Once By Content Hash' reads like a one-time task, not a repeatable behaviour.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1695): Story `Reattach A Screen Once Its Change Reaches Production`: Story 'Reattach A Screen Once Its Change Reaches Production' reads like a one-time task, not a repeatable behaviour.

### `branch-on-mechanical-uniqueness`

Rule text: [stories/stories.md:84](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L84)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1326): SubEpic `Author Scenarios And Steps`: Stories under 'Author Scenarios And Steps' share the same verb 'add,'; split by distinct mechanics or merge.

### `conforms-to-schema`

Rule text: a graph rule, written in no practice document

**Graph violations:** 25

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L599): SubEpic `Review Files In Viewer`: SubEpic 'Review Files In Viewer' has no decomposedInto relationship to Epic | SubEpic | Story, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L47): Then `then the queue answers ++Write the scenarios++ with those three steps, in that order, none done`: Then 'then the queue answers ++Write the scenarios++ with those three steps, in that order, none done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L48): Then `and ++Run the unit tier++ still has no steps`: Then 'and ++Run the unit tier++ still has no steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L54): Then `then the queue answers ++Write the scenarios++ with ++Read the epic++ done, ++Write the stories++ being worked and ++Validate the scenarios++ pending`: Then 'then the queue answers ++Write the scenarios++ with ++Read the epic++ done, ++Write the stories++ being worked and ++Validate the scenarios++ pending' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L60): Then `then the queue answers ++Write the scenarios++ with only ++Read the epic++ done and ++Validate the scenarios++ pending`: Then 'then the queue answers ++Write the scenarios++ with only ++Read the epic++ done and ++Validate the scenarios++ pending' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L67): Then `then the agent is told the queue holds no prompt z, only ++Write the scenarios++`: Then 'then the agent is told the queue holds no prompt z, only ++Write the scenarios++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L68): Then `and the queue still holds ++Write the scenarios++ with no steps`: Then 'and the queue still holds ++Write the scenarios++ with no steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L76): Then `then the queue answers ++Write the scenarios++ with ++Read the epic++ done and the other two not done`: Then 'then the queue answers ++Write the scenarios++ with ++Read the epic++ done and the other two not done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L82): Then `then the queue answers ++Write the scenarios++ with every step done`: Then 'then the queue answers ++Write the scenarios++ with every step done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L83): Then `and ++Write the scenarios++ stays on the queue until the agent marks it done with prompt-queue.done, as in Work Through Prompt Queue`: Then 'and ++Write the scenarios++ stays on the queue until the agent marks it done with prompt-queue.done, as in Work Through Prompt Queue' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L89): Then `then the agent is told ++Write the scenarios++ has three steps`: Then 'then the agent is told ++Write the scenarios++ has three steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L90): Then `and ++Write the scenarios++ still has no step done`: Then 'and ++Write the scenarios++ still has no step done' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L100): Then `then the queue answers ++Write the scenarios++ with those three steps, ++Read the epic++ being worked`: Then 'then the queue answers ++Write the scenarios++ with those three steps, ++Read the epic++ being worked' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L101): Then `and the queue box shows ++Write the scenarios++ with them, as in Show Prompt Steps In Queue`: Then 'and the queue box shows ++Write the scenarios++ with them, as in Show Prompt Steps In Queue' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L107): Then `then the queue answers ++Write the scenarios++ with ++Read the epic++ done and ++Write the stories++ being worked`: Then 'then the queue answers ++Write the scenarios++ with ++Read the epic++ done and ++Write the stories++ being worked' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L114): Then `then the queue beside ++Fix the Files app++ tells the agent to set the steps of ++Write the scenarios++ when it takes it and to mark each one done as it goes`: Then 'then the queue beside ++Fix the Files app++ tells the agent to set the steps of ++Write the scenarios++ when it takes it and to mark each one done as it goes' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L122): Then `then the queue holds ++Fix the Files app++ first, marked running, then ++Run the unit tier++`: Then 'then the queue holds ++Fix the Files app++ first, marked running, then ++Run the unit tier++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L123): Then `and ++Fix the Files app++ is the working prompt its steps are copied onto, as in Copy Task List Onto Working Prompt`: Then 'and ++Fix the Files app++ is the working prompt its steps are copied onto, as in Copy Task List Onto Working Prompt' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L129): Then `then the queue still holds only ++Write the scenarios++`: Then 'then the queue still holds only ++Write the scenarios++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L130): Then `and ++Write the scenarios++ is the working prompt`: Then 'and ++Write the scenarios++ is the working prompt' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L138): Then `then ++Write the scenarios++' card shows 1/3`: Then 'then ++Write the scenarios++' card shows 1/3' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L139): Then `and ++Run the unit tier++'s card shows no progress`: Then 'and ++Run the unit tier++'s card shows no progress' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L145): Then `then ++Read the epic++, ++Write the stories++ and ++Validate the scenarios++ show under its card, in order`: Then 'then ++Read the epic++, ++Write the stories++ and ++Validate the scenarios++ show under its card, in order' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L146): Then `and ++Read the epic++ is ticked and ++Write the stories++ is marked as being worked`: Then 'and ++Read the epic++ is ticked and ++Write the stories++ is marked as being worked' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\queue-prompts-for-later\nest-prompt-steps-in-queue\nest_prompt_steps_in_queue_story.test.md#L152): Then `then only the card of ++Write the scenarios++ shows, with 1/3`: Then 'then only the card of ++Write the scenarios++ shows, with 1/3' has no observes relationship to Example, which the stories practice schema requires.

### `four-to-nine-children`

Rule text: [stories/stories.md:82](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L82)

**Graph violations:** 13

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L447): SubEpic `Customize Board Workflow`: sub-epic 'Customize Board Workflow': 2 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L495): SubEpic `Show Board Quickly`: sub-epic 'Show Board Quickly': 3 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L705): SubEpic `Steer Sessions`: sub-epic 'Steer Sessions': 11 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L751): SubEpic `Guide Work Through Practices In Chat Bar`: sub-epic 'Guide Work Through Practices In Chat Bar': 11 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L837): SubEpic `Review Fidelity Outputs In Chat Bar`: sub-epic 'Review Fidelity Outputs In Chat Bar': 3 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L889): SubEpic `Capture Session Knowledge`: sub-epic 'Capture Session Knowledge': 3 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L939): Epic `Queue Prompts For Later`: epic 'Queue Prompts For Later': 11 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L979): SubEpic `Work Through Prompt Queue`: sub-epic 'Work Through Prompt Queue': 3 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1271): SubEpic `View Story Map`: sub-epic 'View Story Map': 2 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1326): SubEpic `Author Scenarios And Steps`: sub-epic 'Author Scenarios And Steps': 2 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1343): SubEpic `Author Examples`: sub-epic 'Author Examples': 3 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1390): SubEpic `Author Story Changes With AI`: sub-epic 'Author Story Changes With AI': 1 children (target 4-9)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L2180): Epic `Connect Sessions Across Channels And Apps`: epic 'Connect Sessions Across Channels And Apps': 3 children (target 4-9)

### `story-name-captures-system-mechanic`

Rule text: [stories/stories.md:81](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L81)

**Graph violations:** 5

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L475): Story `Run Work Type Flows`: Story 'Run Work Type Flows' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L834): Story `Run Fidelity Action With Overlays`: Story 'Run Fidelity Action With Overlays' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1312): Story `Manage Increments`: Story 'Manage Increments' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1320): Story `Manage Increment Stories`: Story 'Manage Increment Stories' names a generic handler; use the system mechanic (e.g. 'Submit Order').
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1715): Story `Run A Scenario's Thens On The Canvas`: Story "Run A Scenario's Thens On The Canvas" names a generic handler; use the system mechanic (e.g. 'Submit Order').

### `story-scenarios-at-most-seven`

Rule text: [stories/stories.md:83](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L83)

**Graph violations:** 10

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L257): Story `Display Board`: story 'Display Board': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L269): Story `Display Ticket Card`: story 'Display Ticket Card': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L273): Story `Display Ticket Details`: story 'Display Ticket Details': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L293): Story `Open Ticket Session`: story 'Open Ticket Session': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L297): Story `Activate Ticket`: story 'Activate Ticket': 10 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L301): Story `Close Active Session`: story 'Close Active Session': 11 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L515): Story `Choose Action And Formats`: story 'Choose Action And Formats': 9 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L667): Story `Open App From Health Panel`: story 'Open App From Health Panel': 12 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1163): Story `Switch Files App To Graph View`: story 'Switch Files App To Graph View': 8 scenarios — story is huge (target 1-7)
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1175): Story `Open Several Files From Graph Nodes`: story 'Open Several Files From Graph Nodes': 9 scenarios — story is huge (target 1-7)

### `verb-noun-format`

Rule text: [stories/stories.md:80](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L80)

**Graph violations:** 8

- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L469): SubEpic `Run Tickets Through Customized Workflow`: SubEpic 'Run Tickets Through Customized Workflow': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L475): Story `Run Work Type Flows`: Story 'Run Work Type Flows': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L834): Story `Run Fidelity Action With Overlays`: Story 'Run Fidelity Action With Overlays': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1312): Story `Manage Increments`: Story 'Manage Increments': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1320): Story `Manage Increment Stories`: Story 'Manage Increment Stories': opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L1715): Story `Run A Scenario's Thens On The Canvas`: Story "Run A Scenario's Thens On The Canvas": opens with a generic verb; judge from its context whether the action is plain.
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L2240): Story `Comment On A Story Card`: Story 'Comment On A Story Card': name should start with a verb (got nominalisation).
- [X] **ERROR** **[graph rule]** - [.context/story-map.md](C:\dev\abd-cdd-simple-queue-enhancement\.context\story-map.md#L2256): Story `Comment On A Story In Story UI`: Story 'Comment On A Story In Story UI': name should start with a verb (got nominalisation).
