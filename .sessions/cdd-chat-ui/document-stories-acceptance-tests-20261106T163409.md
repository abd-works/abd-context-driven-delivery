# Stories acceptance tests — documented state

**Guidance:** stories-acceptance-tests · **Session:** cdd-chat-ui · **Scanned:** `C:/dev/abd-cdd-cdd-chat-ui/harness/chat-ui/pane/test` at commit `9b26a27dd` on branch cdd-chat-ui.

This records what the chat bar's acceptance tests do today and flags each place they break a rule. Nothing was corrected.

## What exists

- **Harness.** `story-test.ts` turns `story` / `scenario` / `given` / `when` / `then` / `and` / `but` into one `claude plugin test` per scenario. Every scenario uses the `CHAT_BAR` lifecycle from `chat-bar-screen.ts`. Its `wire` stubs the engine and the cdd server before any step. Its `mount` starts the chat, submits one prompt, and mounts the bar once the Givens have run. Infrastructure therefore stays out of the Givens.
- **Stub.** `cdd-stub.ts` stands in for the cdd MCP server. `board.show` answers the seeded `world.board`. Five ticket tools (`move_next`, `finish_review`, `close`, `activate`, `create`) change that board the way the Python Ticket does. Every other tool answers from `world.answers` and fails with the text in `world.refusals`. Calls are recorded so a Then can read what the pane sent.
- **Examples.** `examples/chat-bar.examples.ts` holds the shared fixtures. Each one is labelled **Seed** (state the cdd server owns, in `TicketData` / `BoardData` shape) or **Interaction** (`NEW_SESSION_NAME`). The fixtures are `checkoutFlow`, `checkoutFlowWith`, `paymentRetry`, `boardOf`, `HEALTHY`, the stage fidelity lists, and the `GENERATED` / `VALIDATED` / `DONE` fidelity states.
- **Stories.** 19 story files under `move-work-forward-from-chat-bar/`, one per story on `harness/chat-ui/.context/story-map.md`, with 38 scenarios in four sub-epics:
  - Check CDD Server Health: 4 stories;
  - See Work In Chat Bar: 4 stories;
  - Steer Sessions: 4 stories;
  - Guide Work Through Practices: 7 stories.

  Each file names its epic, sub-epic, map anchor and model. Each step carries its realization as a `//` call-graph comment. Every map story links to its test file.

## Followed

- **`examples-declare-seed-vs-interaction`:** every export in the examples file says Seed or Interaction.
- **`infrastructure-in-lifecycle-hooks`:** engine wiring and mounting sit in `CHAT_BAR.wire` / `mount`, not in Givens.
- **`seed-state-at-its-real-owner`:** board and ticket state is seeded on the stubbed cdd server (`scene.world.board`), never on the pane.
- **`separate-test-controls-from-production-contracts`:** seeding and inspection (`world`, `called`, `dueTimers`) live in the test stub; production hooks have none.
- **`system-stubs-domain-real`:** the pane's own clients run for real; only the MCP boundary is stubbed.
- **`assert-domain-behavior-not-seeded-state`:** most Thens read the drawn bar, or the outbound call, after a press made the pane act.
- **`inline-simple-gwt-bodies`:** most step bodies are one to three lines.
- **Helpers:** the shared ones are screen gestures and reads (`markOf`, `tipOf`, `expectMarks`, `expectMarkLooks`, `expectMarkColours`), which this rule allows.

## Violations

### `system-stubs-domain-real`

- **Refusal text:** `view_fidelity_files_story.test.ts:37` refuses with `../secrets.txt is not a file in this repository`. The real server refuses with `PathOutsideRootsError`, "../secrets.txt is outside the session's roots" (`harness/kanban/review-fidelity-outputs.story.shared.py:175`). The scenario's Then (line 44) asserts the invented text, so the test passes against wording production never sends.
- **Canned answers:** `ticket.files`, `ticket.read_file`, `ticket.report` and `ticket.workspace` answer whatever a Given writes into `world.answers`. The stub does not reproduce these operations. For example, `ticket.files` answers the same canned map whatever fidelity is asked for, so the pane asking for the wrong fidelity would still pass. Only the `called(...)` check in the Then (`list_session_files_story.test.ts`) guards this.
- **Next action with violations:** `withNextActions` in the examples names **review** as the next action while a fidelity has violations. That matches this branch's Python (`harness/kanban/ticket.py:196`), but main now names **satisfy** (FidelityProgress.next_action). `review_fidelity_story.test.ts` "Refuse a review before a clean validate" depends on the old answer, and its When comment says so.

### `assert-domain-behavior-not-seeded-state`

- `display_stage_strip_story.test.ts:54` "Redraw after the agent moves the session": the When writes the moved board into the stub by hand, then fires an engine `tool.call`. The Then reads Implementation back from the state the When seeded. Nothing proves the pane read the board again because of the tool call, rather than the board having changed underneath it.

### `when-holds-the-operation`

These Whens assert before they act, so a failure in them reads as the operation failing:
- `move_session_to_next_stage_story.test.ts:22`;
- `review_fidelity_story.test.ts:23`;
- `review_fidelity_story.test.ts`, "Refuse a review…": the When also selects the dot first.

### `given-only-what-the-system-checks` / `context-setup-expresses-state`

- **Givens that assert:** `display_server_health_mark_story.test.ts:29` ("the Chat Bar shows checkout-flow") and `reinstall_cdd_tools_story.test.ts:16` assert in the Given instead of establishing state.
- **Label and setup disagree:** `view_fidelity_files_story.test.ts:35` says "checkout-flow's repository is the project folder", but its body seeds a `../secrets.txt` file and a refusal.
- **Given that seeds nothing:** `open_server_health_panel_story.test.ts:45` ("the server health panel is open over the mark") has no body. Its When's one press opens the panel rather than pinning it, so the scenario never establishes the pinned state it names.

### `browser-then-asserts-screen-widgets`

- `reinstall_cdd_tools_story.test.ts:26` "the panel says installing while the installer runs" asserts the installer's argv, not the panel. The comment says the test kit cannot draw while an engine call is pending and leaves the line to the heavy surface spec.

### `shared-example-fixtures`

- **Copied answer:** the declared-files answer for clean_engineering-model (`chat-bar-client.ts`, `fidelity-client.ts`) is written out twice, at `list_session_files_story.test.ts:21` and `view_fidelity_files_story.test.ts:19`.
- **Inline answers:** the read-file text and the `ticket.report` answer (`view_fidelity_files_story.test.ts`) are inline literals, not named example fixtures.

### `extract-assertion-helper`

- Reading a fidelity's card state, `textOf((await drawn(ui, 'card-cell-<slug>'))?.children?.[2])`, repeats in four files: display_stage_fidelities, move_session_to_next_stage, display_session_card and review_fidelity. It has no helper beside `expectMarks`.

### Story naming (`story-name-captures-system-mechanic`, carried from story_map)

- **Open Board:** the story and its file are named "Open Board", but the map (story-map.md line 54) says pressing a dot now only selects the fidelity and nothing opens the board. Its one scenario tests dot selection.

## Smaller observations

- **Unused imports:** `cdd` is imported and not used in three files: display_server_health_mark, open_server_health_panel and display_stage_strip.
- **Bodiless Givens:** several, such as "cdd answers server-health.report with 116 tools loaded" and "cdd is connected", rely on the stub's defaults (`HEALTHY`, 116 tools, checkout-flow active). That is true of the default world, but the default isn't named in the step.
- **Before the merge:** this branch predates the Ticket refactor merged into ensure-domain-orientation-refactor. That merge already moved these tests and the stub to `fidelity-progress.*`, `session.read_file`, `board.activate` / `board.workspace` and nested ticket data. The violations above describe this branch as it is.
