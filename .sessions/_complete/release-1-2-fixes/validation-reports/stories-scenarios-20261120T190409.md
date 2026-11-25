# Graph rule validation

**Generated:** 2026-11-20 19:04:52 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-scenarios-20261120T190409\graph.json`

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

**Total graph violations:** 23
**Rules with graph hits:** 4
**AI rules in scope:** 46

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

### `scenarios-name-a-story-on-the-map`

Rule text: [stories/stories.md:149](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L149)

### `given-only-what-the-system-checks`

Rule text: [stories/stories.md:150](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L150)

### `given-names-complex-state-root-first`

Rule text: [stories/stories.md:151](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L151)

### `but-marks-missing-state`

Rule text: [stories/stories.md:152](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L152)

### `when-holds-the-operation`

Rule text: [stories/stories.md:153](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L153)

### `when-names-intent-not-interface-gesture`

Rule text: [stories/stories.md:154](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L154)

### `expressive-system-interactions`

Rule text: [stories/stories.md:155](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L155)

### `and-chaining`

Rule text: [stories/stories.md:156](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L156)

### `outline-requires-many-permutations`

Rule text: [stories/stories.md:157](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L157)

### `plain-english-gwt-steps`

Rule text: [stories/stories.md:158](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L158)

### `seed-prior-story-as-given`

Rule text: [stories/stories.md:159](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L159)

### `domain-terms-link-to-model`

Rule text: [stories/stories.md:160](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L160)

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

**Graph violations:** 2

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\graph_reading.py#L247): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.
- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/graph_reading.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\graph_reading.py#L294): Operation `__init__`: Operation '__init__' duplicates the body of '__init__'.

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

### `conforms-to-schema`

Rule text: a graph rule, written in no practice document

**Graph violations:** 19

- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L53): Then `then ++bookshop/.context/ux-context.md++ holds the same scope, invariant and note`: Then 'then ++bookshop/.context/ux-context.md++ holds the same scope, invariant and note' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L61): Then `then ++bookshop/.context/information-architecture.drawio++ is as it was, with its four screens and their transitions`: Then 'then ++bookshop/.context/information-architecture.drawio++ is as it was, with its four screens and their transitions' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L70): Then `then ++bookshop/.context/ux-context.md++ holds `Scope: Place New Order``: Then 'then ++bookshop/.context/ux-context.md++ holds `Scope: Place New Order`' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L71): Then `and it still holds its invariant`: Then 'and it still holds its invariant' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L79): Then `then Book Details shows the stories Add Book To Cart and View Book`: Then 'then Book Details shows the stories Add Book To Cart and View Book' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L80): Then `and it names the domain terms Book and Cart Line`: Then 'and it names the domain terms Book and Cart Line' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L81): Then `and each other screen has the stories of the ++callout++ under its own box`: Then 'and each other screen has the stories of the ++callout++ under its own box' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L89): Then `then Book Details has the layout split-screen`: Then 'then Book Details has the layout split-screen' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L90): Then `and its regions fill the areas panel and body`: Then 'and its regions fill the areas panel and body' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L91): Then `and the transition Check out is a top nav`: Then 'and the transition Check out is a top nav' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L99): Then `then Book Details has the regions Book Summary and Add To Cart, and no other`: Then 'then Book Details has the regions Book Summary and Add To Cart, and no other' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L100): Then `and Add To Cart holds Quantity (number), then the buttons Add to cart and Back to list`: Then 'and Add To Cart holds Quantity (number), then the buttons Add to cart and Back to list' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L101): Then `and Payment holds Street (text), Country (dropdown), Save this card (checkbox), then the button Pay`: Then 'and Payment holds Street (text), Country (dropdown), Save this card (checkbox), then the button Pay' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L109): Then `then Add To Cart holds Quantity with no type, then the buttons Add to cart and Back to list`: Then 'then Add To Cart holds Quantity with no type, then the buttons Add to cart and Back to list' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L117): Then `then each control still has its states, its interactions and its story steps`: Then 'then each control still has its states, its interactions and its story steps' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L125): Then `then UX works in typescript, one of the formats that fidelity writes`: Then 'then UX works in typescript, one of the formats that fidelity writes' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L133): Then `then the render is refused: UX front-end views are written by hand, not rendered`: Then 'then the render is refused: UX front-end views are written by hand, not rendered' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L134): Then `and ++bookshop/src/CheckoutView.tsx++ is not read as a mockup page`: Then 'and ++bookshop/src/CheckoutView.tsx++ is not read as a mockup page' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/deliver-work-with-context-guidance/produce-formal-artifacts/take_ux_map_to_another_format_and_back_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\deliver-work-with-context-guidance\produce-formal-artifacts\take_ux_map_to_another_format_and_back_story.test.md#L142): Then `then `bookshop/src/CheckoutView.jsx` holds the same ++view++`: Then 'then `bookshop/src/CheckoutView.jsx` holds the same ++view++' has no observes relationship to Example, which the stories practice schema requires.

### `limit-operation-parameters`

Rule text: [clean_engineering/clean_engineering.md:242](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L242)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/drawio/nodes.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\drawio\nodes.py#L353): Operation `_append_transition`: Operation '_append_transition' takes 4 parameters (maximum 3, excluding self).

### `prefer-class-operations`

Rule text: [clean_engineering/clean_engineering.md:235](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\clean_engineering\clean_engineering.md#L235)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [cdd_guidance/practices/ux/model/drawio/nodes.py](C:\dev\abd-cdd-release-1-2-fixes\cdd_guidance\practices\ux\model\drawio\nodes.py#L413): OoadClass `Callout`: Module function '_corner' (line 413) is only used from 'Callout'. Move it onto 'Callout' as a method.
