# Graph rule validation

**Generated:** 2026-11-18 03:18:40 UTC
**Project:** abd-cdd-simple-queue-enhancement
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-simple-queue-enhancement\.sessions\simple-queue-enhancements\.context\checked-graphs\stories-scenarios-20261118T031831\graph.json`

**The session's graph also held, and practice-wide rules compared against:**
- `.context`
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
- `story_tests/review-generated-work-in-file-viewer`

## Summary

**Total graph violations:** 42
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

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L70): Then `but their own children stay hidden until they are opened`: But step should mark missing or absent state, not a consequence: 'their own children stay hidden until they are opened'.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L175): Then `but Ticket in ticket.py carries none, since LERN applies only to TypeScript`: But step should mark missing or absent state, not a consequence: 'Ticket in ticket.py carries none, since LERN applies only to TypeScript'.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L230): Then `but a line inside Ticket that names the class Board still opens Board`: But step should mark missing or absent state, not a consequence: 'a line inside Ticket that names the class Board still opens Board'.

### `when-holds-the-operation`

Rule text: [stories/stories.md:150](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L150)

### `when-names-intent-not-interface-gesture`

Rule text: [stories/stories.md:151](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L151)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L123): When `when the Person presses Filters`: When step 'the Person presses Filters' names a UI gesture; state the domain intent instead.

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

**Graph violations:** 38

- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L63): Then `then the Stories and Clean Engineering practice trees show collapsed`: Then 'then the Stories and Clean Engineering practice trees show collapsed' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L69): Then `then Ticket shows its operations, such as Ticket.activate and Ticket.close`: Then 'then Ticket shows its operations, such as Ticket.activate and Ticket.close' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L70): Then `but their own children stay hidden until they are opened`: Then 'but their own children stay hidden until they are opened' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L76): Then `then Ticket shows the Graph app's class mark`: Then 'then Ticket shows the Graph app's class mark' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L77): Then `and Ticket.activate and Ticket.close show its operation mark`: Then 'and Ticket.activate and Ticket.close show its operation mark' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L92): Then `then Ticket.delete shows an invokes group holding Board.reread`: Then 'then Ticket.delete shows an invokes group holding Board.reread' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L98): Then `then board.py opens beside ticket.py, at Board.reread`: Then 'then board.py opens beside ticket.py, at Board.reread' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L117): Then `then the graph view shows one closed Filters toggle above the practice trees`: Then 'then the graph view shows one closed Filters toggle above the practice trees' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L118): Then `but not the node type, connector and rule lists or the Violations switch, so the trees get the space`: Then 'but not the node type, connector and rule lists or the Violations switch, so the trees get the space' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L124): Then `then the node type, connector and rule lists and the Violations switch show above the trees`: Then 'then the node type, connector and rule lists and the Violations switch show above the trees' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L125): Then `and the graph view opens with them shown the next time this browser opens it, until the Person presses Filters again`: Then 'and the graph view opens with them shown the next time this browser opens it, until the Person presses Filters again' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L131): Then `then the Clean Engineering tree holds Ticket.activate, Ticket.close, Ticket.delete and Board.reread`: Then 'then the Clean Engineering tree holds Ticket.activate, Ticket.close, Ticket.delete and Board.reread' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L132): Then `and the connectors and rules offered narrow to the ones operations carry`: Then 'and the connectors and rules offered narrow to the ones operations carry' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L138): Then `then the tree holds Ticket.delete and Board.reread`: Then 'then the tree holds Ticket.delete and Board.reread' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L139): Then `but not Ticket.activate or Ticket.close, which invoke none of the operations listed`: Then 'but not Ticket.activate or Ticket.close, which invoke none of the operations listed' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L145): Then `then the Clean Engineering tree holds Ticket.activate, Ticket.close and Ticket.delete`: Then 'then the Clean Engineering tree holds Ticket.activate, Ticket.close and Ticket.delete' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L146): Then `but not Board.reread, whose file the list leaves out`: Then 'but not Board.reread, whose file the list leaves out' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L152): Then `then Board.reread joins the Clean Engineering tree`: Then 'then Board.reread joins the Clean Engineering tree' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L153): Then `and the graph stays filtered to operations`: Then 'and the graph stays filtered to operations' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L159): Then `then the graph view holds every node of the files listed again`: Then 'then the graph view holds every node of the files listed again' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L174): Then `then Ticket in ticket.ts carries LERN's Domain tier rules among its rules`: Then 'then Ticket in ticket.ts carries LERN's Domain tier rules among its rules' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L175): Then `but Ticket in ticket.py carries none, since LERN applies only to TypeScript`: Then 'but Ticket in ticket.py carries none, since LERN applies only to TypeScript' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L181): Then `then the LERN rules on Ticket in ticket.ts leave the graph view`: Then 'then the LERN rules on Ticket in ticket.ts leave the graph view' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L182): Then `and the chat bar's LERN chip shows off`: Then 'and the chat bar's LERN chip shows off' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L197): Then `then the graph view shows the load step the cdd server reports and how long it has run`: Then 'then the graph view shows the load step the cdd server reports and how long it has run' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L198): Then `and shows the practice trees once the load ends`: Then 'and shows the practice trees once the load ends' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L204): Then `then the graph view shows the server's reason and its traceback instead of loading forever`: Then 'then the graph view shows the server's reason and its traceback instead of loading forever' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L205): Then `and offers a copy of them for the chat`: Then 'and offers a copy of them for the chat' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L220): Then `then the lines of Board.reread, from board.py, show in place below the call`: Then 'then the lines of Board.reread, from board.py, show in place below the call' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L221): Then `and ticket.py stays open where it was`: Then 'and ticket.py stays open where it was' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L229): Then `then no line inside Ticket opens Ticket in place`: Then 'then no line inside Ticket opens Ticket in place' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L230): Then `but a line inside Ticket that names the class Board still opens Board`: Then 'but a line inside Ticket that names the class Board still opens Board' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L238): Then `then the call `self.close()` opens Ticket.close in place below it`: Then 'then the call `self.close()` opens Ticket.close in place below it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L239): Then `and the call `reread_all(board)` opens the function reread_all in place below it`: Then 'and the call `reread_all(board)` opens the function reread_all in place below it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L245): Then `then the call `self.close()` opens that project's Ticket.close in place below it, not the CDD checkout's`: Then 'then the call `self.close()` opens that project's Ticket.close in place below it, not the CDD checkout's' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L253): Then `then the lines of Ticket.close show in place below the call, at their full height`: Then 'then the lines of Ticket.close show in place below the call, at their full height' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L254): Then `and the page grows by those lines, so it scrolls down to them`: Then 'and the page grows by those lines, so it scrolls down to them' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/review-generated-work-in-file-viewer/explore-graph-in-files-app/explore_graph_in_files_app_story.test.md](C:\dev\abd-cdd-simple-queue-enhancement\story_tests\review-generated-work-in-file-viewer\explore-graph-in-files-app\explore_graph_in_files_app_story.test.md#L260): Then `then its calls show as written, with no fold to open them`: Then 'then its calls show as written, with no fold to open them' has no observes relationship to Example, which the stories practice schema requires.
