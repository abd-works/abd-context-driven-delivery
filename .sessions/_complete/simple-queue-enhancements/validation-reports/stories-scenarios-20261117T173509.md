# Graph rule validation

**Generated:** 2026-11-17 17:35:36 UTC
**Project:** abd-cdd-simple-queue-enhancement
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-context-driven-delivery\.sessions\simple-queue-enhancements\.context\checked-graphs\stories-scenarios-20261117T173509\graph.json`

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

**Total graph violations:** 24
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

### `conforms-to-schema`

Rule text: a graph rule, written in no practice document

**Graph violations:** 24

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

## Judgment — `story_tests/queue-prompts-for-later/nest-prompt-steps-in-queue/nest_prompt_steps_in_queue_story.test.md`

### `conforms-to-schema` — Fail
- nest_prompt_steps_in_queue_story.test.md:47 Every Then (24, lines 47 to 152) has no observes link to an Example. The examples tables sit at the top of the file under `## Examples`, and the markdown reader gives such file-level rows to no scenario (the Files app's switch scenarios parse the same way), so no Example node is made from this file. The link is made from a story test's examples module, which the next fidelity (acceptance tests in Python) writes; until then these stand.

### `when-holds-the-operation` — Fail
- nest_prompt_steps_in_queue_story.test.md:137 Was "When the person looks at the queue", a glance, not an operation; changed after this run to "opens the prompt queue". Line 128 was "a turn ends and the chat is sent …", two events in one When; changed to "play asks the agent to take the next prompt on the queue". Both need the next run to confirm.

Passes: vocabulary-traces-to-domain-source (prompt queue, queued prompt, step, working prompt, task list as defined at the top, matching Work Through Prompt Queue's terms); read-all-source-context-in-full (the queue epic, the Work Through Prompt Queue scenarios, `prompt_queue.py` and the mod were read; sources named on the map); do-not-invent-requirements (each story is one of the four parts the person agreed on 2026-11-17; the refusals cover the tools' bad input, and folding the steps away is the other half of "opens to its steps"); flagged-writes-intended-gwt (every scenario is marked Intended, and Copy Task List Onto Working Prompt names the missing evidence: whether a mod's hook sees `update_plan`); scenario-names-continuation (Thens name Work Through Prompt Queue, Show Prompt Steps In Queue and Copy Task List Onto Working Prompt where the flow continues); but-marks-missing-state (But marks the prompt with no steps and the missing prompt z); and-chaining; plain-english-gwt-steps; behavioral-and-system-observable-outcomes (each Then is what the queue answers, what the agent is told, or what the box shows); explore-full-interaction-surface; given-only-what-the-system-checks; given-names-complex-state-root-first (the queue, then its prompt, then its steps); outline-requires-many-permutations (no outline: each variation changes the flow); seed-prior-story-as-given; expressive-system-interactions; when-names-intent-not-interface-gesture; examples-trace-domain-model; reconcile-live-immediately (nothing built yet to reconcile); domain-terms-link-to-model (no class-model.md for the queue, so terms stay unlinked); gwt-steps-trace-to-domain-operations (each step names a queue operation the Python side will hold: set steps, mark a step done, done).
