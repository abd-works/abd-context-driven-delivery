# Validate

Take the persona of a **critical judge** — do not edit the artifact.

1. Read the appropriate practice and fidelity level guidlines and rules. Scope judgment to artifacts passed into context.
2. Use each **practice** as the rubric — report Pass or Fail per named practice fidelity and named rule with brief evidence. There is no third verdict: a rule that is only partly met is a Fail, because a softer verdict lets a broken rule through review.
3. When **paths** names the files being edited, the graph is built from just those files as they are now, and its rules run on them. Pass the files you wrote, not the whole tree. Without **paths**, when **graph** is `true`, read the workspace's saved graph (`.context/graph.json`, written by `graph_load_working_copy`); when it is a path (or list of paths), read that `graph_return_nodes` JSON or saved graph. Append a **Graph rule validation** report for each guidance's practice. Each rule is one section: heading, rule text, any graph hits (**[graph rule]**), then the AI judgment prompt for that rule.
4. Collection validate on graph-backed practices reads the working copy and reports each rule hit. A single base Rule is instruction text only.
5. Do not fix. Report failures for fixing, then add your judgment for each rule to the report this action saved, so the board links to the whole result. It names the report's path at the end of its reply.
6. Write the judgment in this shape, because the session board reads it and lists each finding beside the graph's hits, with a Fix that sends it back:

   ```markdown
   ## Judgment — `path/of/the/judged/file.md`

   ### `rule-slug` — Fail
   - story-map.md:86 `Archive Ticket`: what breaks the rule, and why.

   ### `other-rule-slug` — Fail
   - story-map.md:148 `Send Sketch Iterate Or Document`: what breaks the rule, and why.
   ```

   One `###` heading per rule that fails, with Fail after the dash. One bullet per finding, opening with the judged file's name and the line, so a person can open the finding at that line. Leave passing rules out of these headings; a table or a Passes paragraph may list them.


### `vocabulary-traces-to-domain-source`

Use terms from the domain language and model when they exist, because one shared definition keeps Stories, examples, and code consistent.

Evaluate the current context against this rule (vocabulary-traces-to-domain-source):

### `read-all-source-context-in-full`

Before fixing the hierarchy or asking a question about an interaction between systems, read every referenced source that informs the decision, including the owning segment, module context, session records, related Story context, build order, code, recorded observations, and relevant run logs. Name the source and location that supports each important interaction, because titles and search results do not explain behaviour.

Evaluate the current context against this rule (read-all-source-context-in-full):

### `do-not-invent-requirements`

Write only behaviour described by a source or explicitly requested by the user. Add a system-to-system interaction only when a named caller invokes it or a source requires it, because an assumed interaction becomes unrequested architecture, Scenarios, and tests.

Evaluate the current context against this rule (do-not-invent-requirements):

### `gwt-steps-trace-to-domain-operations`

Map every Given, When, and Then to a named domain operation or property. Express continuation as an operation on the aggregate that receives control, because routes, waits, and framework calls do not describe domain behaviour.

Evaluate the current context against this rule (gwt-steps-trace-to-domain-operations):

### `behavioral-and-system-observable-outcomes`

Write each Then as a result a person or another system can observe, such as changed information, a returned response, or a changed interface state. Keep internal flags and function-local state out of Then, because they do not prove delivered behaviour.

Evaluate the current context against this rule (behavioral-and-system-observable-outcomes):

### `explore-full-interaction-surface`

Before finalizing Scenarios and again before generating acceptance tests, inspect every distinct visible behaviour required by the source or running product. Add Scenarios for distinct mechanics, because a happy path cannot protect validation and failure behaviour.

Evaluate the current context against this rule (explore-full-interaction-surface):

### `examples-trace-domain-model`

Provide an example for every domain concept the scenario mentions. Use that concept's own terms and the values the source gives, because a step that names a concept without an example leaves the behaviour unagreed.

Evaluate the current context against this rule (examples-trace-domain-model):

### `reconcile-live-immediately`

In brownfield work, update the map and Scenario in the same increment when the running product contradicts the current description. Mark intended changes separately, because observed and desired behaviour are different evidence.

Evaluate the current context against this rule (reconcile-live-immediately):

### `flagged-writes-intended-gwt`

When available evidence cannot exercise required behaviour, write the intended Given, When, and Then and state what evidence is missing, because an evidence gap must not erase the requirement or turn an expectation into an observed fact.

Evaluate the current context against this rule (flagged-writes-intended-gwt):

### `scenario-names-continuation`

Put the main flow first and make each continuing Then name the next Story on the map. Add a missing map node when a live path continues without one, because Scenarios are alternate flows within Stories rather than substitutes for Stories.

Evaluate the current context against this rule (scenario-names-continuation):

### `given-only-what-the-system-checks`

Describe the activity and state that the system actually uses for this behaviour, including state left by a prior Story. Omit off-system history, orphan data, screen names used as state, and fields the decision never reads, because irrelevant setup hides the real preconditions.

Evaluate the current context against this rule (given-only-what-the-system-checks):

### `given-names-complex-state-root-first`

Begin complex Given state with the aggregate root, then describe its owned parts in their current state, because an owned entity does not have independent context outside its aggregate.

Evaluate the current context against this rule (given-names-complex-state-root-first):

### `but-marks-missing-state`

Use But for a record that is absent or an action the actor did not take; use And for consequences of that absence and name gated operations as enabled or disabled, because But should identify the missing condition rather than its effects.

Evaluate the current context against this rule (but-marks-missing-state):

### `when-holds-the-operation`

Put the operation under test in When and, in Then, assert only results it has already produced. For downstream system Stories, describe the request arriving at that system instead of replaying the original user action. Specify enablement and activation as separate behaviours when both are observable, because triggers inside assertions and combined operations hide which action caused the result.

Evaluate the current context against this rule (when-holds-the-operation):

### `when-names-intent-not-interface-gesture`

Name the actor's domain intent and subject rather than the button or gesture used to express it. Keep click and tap details in UX artifacts unless the physical interaction is required behaviour, because controls can change while intent remains stable.

Evaluate the current context against this rule (when-names-intent-not-interface-gesture):

### `expressive-system-interactions`

Describe each system's When and Then in that system's vocabulary. A caller's Then names the result it receives; a translating intermediary names the incoming caller concept and the returned caller-facing result, because "calls the service" does not explain the work performed.

Evaluate the current context against this rule (expressive-system-interactions):

### `and-chaining`

Start each state, interaction, and result block with Given, When, and Then, then continue later steps of the same kind with And. Keep Given conditions in root-first order, start a new When for a new interaction, and keep one interaction's observable results in one Then/And block. Use Background only when more than one Scenario shares the state, because repeated keywords hide which conditions, actions, and results belong together.

Evaluate the current context against this rule (and-chaining):

### `outline-requires-many-permutations`

Use a Scenario Outline when many data combinations follow the same steps. Use separate steps or Scenarios for two alternatives or a changed flow, and keep only example fields that affect behaviour, because examples should show variation rather than conceal structure.

Evaluate the current context against this rule (outline-requires-many-permutations):

### `plain-english-gwt-steps`

Write each step as a readable sentence with a named actor and observable behaviour. Use the plain-English example name rather than a code identifier, because test reports must make sense without source code.

Evaluate the current context against this rule (plain-english-gwt-steps):

### `seed-prior-story-as-given`

Seed a later Story from examples produced by prior Stories instead of replaying their When steps. Reuse fixtures from the owning domain concept and keep the boundary under test real, because each Story must run independently while proving its own behaviour.

Evaluate the current context against this rule (seed-prior-story-as-given):

### `domain-terms-link-to-model`

Link each domain term in Given, When, and Then text and in example tables to its definition in the domain model markdown, `domain-model.md` (DDD) or `class-model.md` (Clean Engineering), anchored at the class or term heading (`domain-model.md#sim-aggregate-root-entity`). With no model file, write the term without a link, because a step that leads to its definition keeps the Scenario and the model on one meaning, and a link to a missing file misleads.

Evaluate the current context against this rule (domain-terms-link-to-model):

# Judgment

Judged: the 40 Scenario files of the session-board story map, `harness/kanban/.context/move-work-forward-on-session-board/**/*_story.test.py`, against the Stories scenarios rules above, with `harness/kanban/.context/kanban-model.md` as the model. This run had no paths and no graph, so there are no graph hits; every finding below is judged. No story file has changed since the judgment on stories-scenarios-20261104T164249; the `_story.test.md` files rendered beside them since then hold the same text, so each finding below applies to the rendered copy too.

**Passes:** `read-all-source-context-in-full`, `do-not-invent-requirements`, `behavioral-and-system-observable-outcomes`, `flagged-writes-intended-gwt`, `given-only-what-the-system-checks`, `given-names-complex-state-root-first`, `expressive-system-interactions`, `and-chaining`, `seed-prior-story-as-given`. Every Scenario carries Evidence, and the inferred ones say which source is missing.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/see-work-on-session-board/display-board/display_board_story.test.py`

### `reconcile-live-immediately` — Fail
- display_board_story.test.py:71 `Restart cdd on the current code`: the Then says the board is read "from a fresh cdd server", and the Evidence at line 63 describes a cdd server of the board's own. Since commit 4771a635 the board and every chat share one cdd server, and Restart cdd reloads it in place; the Scenario still describes the old product.

### `when-holds-the-operation` — Fail
- display_board_story.test.py:83 `Keep the newer board when an older read answers late`: one When holds two operations, another chat moving move-me and the board reading again, so the Then cannot say which one caused the result.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/see-work-on-session-board/display-ticket-details/display_ticket_details_story.test.py`

### `vocabulary-traces-to-domain-source` — Fail
- display_ticket_details_story.test.py:88 `Open a card on the fidelity of a pressed block`: the Scenario says block where the code and its own Evidence say segment (`OpenCardClient.openSegment`, `SegmentsView`, 'with a segment pressed'). Lines 90 and 92 repeat block, and Display Ticket Card's card Scenario uses block too.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/see-work-on-session-board/restrict-actions-to-active-session/restrict_actions_to_active_session_story.test.py`

### `when-holds-the-operation` — Fail
- restrict_actions_to_active_session_story.test.py:20 `Lock tickets that are not the active session`: "the Person looks at billing-report's card and tiles" is not an operation; what is tested is how the board draws a locked ticket. The same "looks at" When appears in Choose Action And Formats, Choose Ticket Practices, Split, Write Ticket Handoff, Send Next Fidelity Action, Validate Fidelity, and Review Fidelity.
- restrict_actions_to_active_session_story.test.py:32 `Keep information and moves open on a locked ticket`: one When holds two operations, opening the files and moving the ticket.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/steer-ticket-sessions/close-active-session/close_active_session_story.test.py`

### `when-names-intent-not-interface-gesture` — Fail
- close_active_session_story.test.py:18 `Close the active session from its card`: "presses Close on checkout-flow's card" names the button; the intent is closing checkout-flow's session.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/steer-ticket-sessions/open-ticket-session/open_ticket_session_story.test.py`

### `but-marks-missing-state` — Fail
- open_ticket_session_story.test.py:41 `Ask a chat to open a ticket`: the But in the Then block brings in a new condition, no chat connected, and its result; that is a Scenario of its own, not a missing record of this one.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/generate-fidelity-outputs/choose-action-and-formats/choose_action_and_formats_story.test.py`

### `outline-requires-many-permutations` — Fail
- choose_action_and_formats_story.test.py:64 `Keep Run off with no chat or on a locked ticket`: one But joins two alternatives with "or" (no chat; a locked ticket). Two alternatives need two steps or two Scenarios, so each result shows which condition it came from.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/steer-ticket-sessions/split-ticket-into-child-tickets/split_ticket_into_child_tickets_story.test.py`

### `outline-requires-many-permutations` — Fail
- split_ticket_into_child_tickets_story.test.py:41 `Keep Split off where nothing can take the prompt`: the Then adds a closed ticket and a locked ticket, two conditions no Given sets up.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/guide-work-through-practices/send-next-fidelity-action/send_next_fidelity_action_story.test.py`

### `outline-requires-many-permutations` — Fail
- send_next_fidelity_action_story.test.py:93 `Keep Run next off where it cannot run`: the Then adds a locked ticket, a condition no Given sets up.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/generate-fidelity-outputs/send-tile-action-to-chat/send_tile_action_to_chat_story.test.py`

### `when-holds-the-operation` — Fail
- send_tile_action_to_chat_story.test.py:25 `Send sketch, iterate, or document as its own command`: one When runs two actions, iterate then document.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/generate-fidelity-outputs/resolve-fidelity-output-paths/resolve_fidelity_output_paths_story.test.py`

### `examples-trace-domain-model` — Fail
- resolve_fidelity_output_paths_story.test.py:18 `Put a fidelity's files under its practice's root`: the example says the fidelity declares markdown `../../../story-map.md`; it declares `story-map.md`, as the Then's /work/tests/story-map.md shows. A link rewrite has leaked into the example value.

### `plain-english-gwt-steps` — Fail
- resolve_fidelity_output_paths_story.test.py:55 `Rename a single-file output and keep a pattern`: the Then states `{story_snake}_story.test.py`, a code template, not a file name a reader can check.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/review-fidelity-outputs/view-fidelity-files/view_fidelity_files_story.test.py`

### `examples-trace-domain-model` — Fail
- view_fidelity_files_story.test.py:24 `Open one tab per format, generated or not`: the tab is named `../../../story-map.md` while the Then above names the tab tests/story-map.md; the same leaked link rewrite.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/steer-ticket-sessions/activate-ticket/activate_ticket_story.test.py`

### `gwt-steps-trace-to-domain-operations` — Fail
- activate_ticket_story.test.py:77 `Cancel the switch`: the When maps to no operation, so nothing ties cancelling to the activation dialog's own behaviour. The same holds for Add Backlog Item line 39 (trying to add with no title) and Set Stage WIP Limit line 51 (typing many).

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/steer-ticket-sessions/archive-ticket/archive_ticket_story.test.py`

### `explore-full-interaction-surface` — Fail
- archive_ticket_story.test.py:18 `Archive a ticket off the board`: only the happy path. `Ticket.load` refuses a ticket name the board does not have (List Ticket Files shows that failure for `ticket.files`), and archiving such a name is not covered.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/generate-fidelity-outputs/generate-fidelity-output/generate_fidelity_output_story.test.py`

### `scenario-names-continuation` — Fail
- generate_fidelity_output_story.test.py:30 `Send the generate command from a tile`: the main flow ends with the chat running the command and names no next Story; it continues into Resolve Fidelity Output Paths. Validate Fidelity line 23 ends the same way without naming Save Validation Report.

## Judgment — `harness/kanban/.context/move-work-forward-on-session-board/validate-fidelity-outputs/open-validation-report/open_validation_report_story.test.py`

### `domain-terms-link-to-model` — Fail
- open_validation_report_story.test.py:16 `Open a fidelity's latest report`: validation report links to `kanban-model.md#validate--guidanceaction`, the Validate action, not a report. The model has no validation report term, so the link leads to the wrong definition. Arrange Side Panel line 49 and Save Validation Report line 24 link it the same way.
