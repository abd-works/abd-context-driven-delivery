# Graph rule validation

**Generated:** 2026-11-20 19:09:09 UTC
**Project:** abd-cdd-release-1-2-fixes
**Action:** validate (graph JSON + AI rules)

**Graph sources:**
- `C:\dev\abd-cdd-release-1-2-fixes\.sessions\release-1-2-fixes\.context\checked-graphs\stories-scenarios-20261120T190836\graph.json`

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

**Total graph violations:** 41
**Rules with graph hits:** 3
**AI rules in scope:** 22

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

**Graph violations:** 3

- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L125): Then `then Pack Order is in the graph once, under the epic the story map gives it`: Long Then 'Pack Order is in the graph once, under the epic the story map gives it' should name the next story on the map when continuing a flow.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L143): Then `then the When "the Shop Clerk packs the Order" invokes `pack` of the Order its story test imports`: Long Then 'the When "the Shop Clerk packs the Order" invokes `pack` of the Order its story test imports' should name the next story on the map when continuing a flow.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L162): Then `then Submit Order is in the graph with its two scenarios, under the epic its story test's folders name`: Long Then "Submit Order is in the graph with its two scenarios, under the epic its story test's folders name" should name the next story on the map when continuing a flow.

### `scenarios-name-a-story-on-the-map`

Rule text: [stories/stories.md:149](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L149)

### `given-only-what-the-system-checks`

Rule text: [stories/stories.md:150](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L150)

### `given-names-complex-state-root-first`

Rule text: [stories/stories.md:151](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L151)

### `but-marks-missing-state`

Rule text: [stories/stories.md:152](C:\Users\jeffa\.cdd\dev\runtime\cdd_guidance\practices\stories\stories.md#L152)

**Graph violations:** 1

- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L160): Given `but ++submit_order_story.test.py++ still specifies it`: But step should mark missing or absent state, not a consequence: '++submit_order_story.test.py++ still specifies it'.

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

### `conforms-to-schema`

Rule text: a graph rule, written in no practice document

**Graph violations:** 37

- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L69): Then `then the package `src` carries a source-parses violation naming ++src/order.py++`: Then 'then the package `src` carries a source-parses violation naming ++src/order.py++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L70): Then `and the class Other of ++src/other.py++ is in the graph`: Then 'and the class Other of ++src/other.py++ is in the graph' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L78): Then `then the class BomOnly is in the graph`: Then 'then the class BomOnly is in the graph' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L79): Then `and no source-parses violation names ++shop/bom.py++`: Then 'and no source-parses violation names ++shop/bom.py++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L98): Then `then Gift Order and Wrap Order are in the graph with their scenarios, under no epic`: Then 'then Gift Order and Wrap Order are in the graph with their scenarios, under no epic' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L99): Then `and each carries a scenarios-name-a-story-on-the-map violation naming ++story_tests/sell-books/take-orders/take_orders_story.test.md++`: Then 'and each carries a scenarios-name-a-story-on-the-map violation naming ++story_tests/sell-books/take-orders/take_orders_story.test.md++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L107): Then `then Place Order and Cancel Order each hold their scenario`: Then 'then Place Order and Cancel Order each hold their scenario' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L108): Then `and no story carries a scenarios-name-a-story-on-the-map violation`: Then 'and no story carries a scenarios-name-a-story-on-the-map violation' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L116): Then `then each story still holds the scenarios its story tests gave it`: Then 'then each story still holds the scenarios its story tests gave it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L117): Then `and the graph holds the nodes and edges it held before the refresh`: Then 'and the graph holds the nodes and edges it held before the refresh' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L125): Then `then Pack Order is in the graph once, under the epic the story map gives it`: Then 'then Pack Order is in the graph once, under the epic the story map gives it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L126): Then `and the scenarios written in markdown and those written in code are all still in the graph`: Then 'and the scenarios written in markdown and those written in code are all still in the graph' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L134): Then `then Cancel Order holds "Cancel a submitted order" and "Keep the total of a cancelled order"`: Then 'then Cancel Order holds "Cancel a submitted order" and "Keep the total of a cancelled order"' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L135): Then `and each scenario is in the file that writes it`: Then 'and each scenario is in the file that writes it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L143): Then `then the When "the Shop Clerk packs the Order" invokes `pack` of the Order its story test imports`: Then 'then the When "the Shop Clerk packs the Order" invokes `pack` of the Order its story test imports' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L144): Then `and the examples `paid_order` and `unpaid_order` are in the graph`: Then 'and the examples `paid_order` and `unpaid_order` are in the graph' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L152): Then `then Add Book To Cart holds one Background, in ++add_book_to_cart_story.test.md++, given by its Given step with the And chained onto it`: Then 'then Add Book To Cart holds one Background, in ++add_book_to_cart_story.test.md++, given by its Given step with the And chained onto it' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L153): Then `and Change Cart Line Quantity holds no Background`: Then 'and Change Cart Line Quantity holds no Background' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L162): Then `then Submit Order is in the graph with its two scenarios, under the epic its story test's folders name`: Then 'then Submit Order is in the graph with its two scenarios, under the epic its story test's folders name' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L163): Then `and it carries a scenarios-name-a-story-on-the-map violation naming ++submit_order_story.test.py++`: Then 'and it carries a scenarios-name-a-story-on-the-map violation naming ++submit_order_story.test.py++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L171): Then `then the graph holds the scenarios a load of the same files holds, those written in code among them`: Then 'then the graph holds the scenarios a load of the same files holds, those written in code among them' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/build_practice_trees_from_source_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\build_practice_trees_from_source_story.test.md#L172): Then `and their steps invoke the operations a load of the same files links them to`: Then 'and their steps invoke the operations a load of the same files links them to' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L50): Then `then `should be paid` invokes `pay` and `is_paid` of the Order in ++src/ordering/order.py++`: Then 'then `should be paid` invokes `pay` and `is_paid` of the Order in ++src/ordering/order.py++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L51): Then `and it invokes nothing in ++ordering/order/order.py++ or ++src/checkout_view.py++`: Then 'and it invokes nothing in ++ordering/order/order.py++ or ++src/checkout_view.py++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L59): Then `then `should total zero` invokes `total` of Cart, the class its describe's setup built `cart` as`: Then 'then `should total zero` invokes `total` of Cart, the class its describe's setup built `cart` as' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L60): Then `and it does not invoke `total` of CartLine`: Then 'and it does not invoke `total` of CartLine' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L68): Then `then `should hold a line for each cart line` invokes the constructor of Order, then `lines` of Order`: Then 'then `should hold a line for each cart line` invokes the constructor of Order, then `lines` of Order' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L69): Then `and it does not invoke `add` of Cart`: Then 'and it does not invoke `add` of Cart' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L77): Then `then the describe `an order` aligns with the Order in ++src/ordering/order.py++`: Then 'then the describe `an order` aligns with the Order in ++src/ordering/order.py++' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L85): Then `then the When invokes `load` of OrderRepository and `pack` of Order in `src/bookshop/order.py``: Then 'then the When invokes `load` of OrderRepository and `pack` of Order in `src/bookshop/order.py`' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L86): Then `and it invokes nothing in `src/bookshop/order.ts` or `ordering/order/order.py``: Then 'and it invokes nothing in `src/bookshop/order.ts` or `ordering/order/order.py`' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L94): Then `then the When names the root Book and the root Cart of `.context/domain-model.md``: Then 'then the When names the root Book and the root Cart of `.context/domain-model.md`' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L95): Then `and each of those roots is named by the When`: Then 'and each of those roots is named by the When' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L103): Then `then the When names no class for that link`: Then 'then the When names no class for that link' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L104): Then `and it still names the root Book, whose link names a heading the model holds`: Then 'and it still names the root Book, whose link names a heading the model holds' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L121): Then `then the example Tiny Tales demonstrates the root Book of `.context/domain-model.md``: Then 'then the example Tiny Tales demonstrates the root Book of `.context/domain-model.md`' has no observes relationship to Example, which the stories practice schema requires.
- [X] **ERROR** **[graph rule]** - [story_tests/map-work-into-knowledge-graph/build-practice-trees-from-source/link_steps_and_observations_to_operations_story.test.md](C:\dev\abd-cdd-release-1-2-fixes\story_tests\map-work-into-knowledge-graph\build-practice-trees-from-source\link_steps_and_observations_to_operations_story.test.md#L129): Then `then the example `paid_order` demonstrates the root Order of `.context/domain-model.md``: Then 'then the example `paid_order` demonstrates the root Order of `.context/domain-model.md`' has no observes relationship to Example, which the stories practice schema requires.
