---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Validate Fidelity Outputs On Board

## Story: Validate Fidelity

#### Scenario: Send the fidelity to validate

*Given* billing-report is the active [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) and a chat is connected
*And* its story map .context/story-map.md is there
*When* the Person validates story_map
*Then* the chat receives the command /actions-validate stories-story-map
*And* Claude Code goes on to Save Validation Report for stories-story-map

#### Scenario: Count Validate done only with no graph-rule violations

*Given* pet-visits' story map is generated
*When* Claude Code validates the story map and finds no graph-rule violation
*Then* the session log ends with validate Stories story_map
*And* the story_map tile marks Validate ✓
*When* Claude Code validates it again and finds actor-named-in-step on map.md line 12
*Then* the session log ends with validate Stories story_map graph-rule actor-named-in-step map.md:12
*And* the story_map tile marks Validate as violations again

#### Scenario: Keep Validate off with nothing to check

*Given* billing-report's story map has no file
*But* nothing is recorded on it
*When* the session board draws the story_map bar
*Then* validate is off

#### Scenario: Allow Validate again on the same output

*Given* checkout-flow's story map has violations
*When* the session board reads checkout-flow
*Then* validate is on for story_map

## Story: Save Validation Report

#### Scenario: Save the report and the graph it checked

*Given* the [session](../../../../../../space/kanban/.context/kanban-model.md#session) checkout-flow has an entity root with a private-method-naming violation
*When* Claude Code validates ddd-tactics on that file
*Then* the validation report is saved as validation-reports/ddd-tactics-20261101T100000.md naming private-method-naming
*And* the graph it checked is saved beside it as ddd-tactics-20261101T100000.json, with the rule hits on its nodes
*And* Claude Code's reply says where the report is saved

#### Scenario: Save one report for each listed guidance

*Given* the session checkout-flow has edited files for ddd-tactics and stories-scenarios
*When* Claude Code validates ddd-tactics and stories-scenarios together
*Then* validation-reports holds one stories-scenarios report and one ddd-tactics report

#### Scenario: Leave an earlier report's graph as it was

*Given* validation-reports holds ddd-tactics-20200101T000000.json
*When* Claude Code validates ddd-tactics again
*Then* ddd-tactics-20200101T000000.json is unchanged

## Story: Open Validation Report

#### Scenario: Open a fidelity's latest report

*Given* checkout-flow's story map has the validation report stories-story-map-20261101T100000.md with its saved graph
*And* the graph names verb-noun-format on .context/story-map.md line 6
*When* the Person opens checkout-flow's story_map report
*Then* the report panel shows .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md
*And* it lists verb-noun-format with one violation at .context/story-map.md line 6 and the source lines around it

#### Scenario: Show every fidelity's violations at once

*Given* checkout-flow has violations
*When* the Person opens checkout-flow's violations from its card
*Then* the report panel shows .sessions/checkout-flow/validation-reports with every rule broken, each naming its fidelity

#### Scenario: Say a report has no saved graph

*Given* the ticket's latest story_map report has no graph saved beside it
*When* the Person opens the story_map report
*Then* the report panel shows the report's text
*And* it says the report has no saved graph in place of saying it has no violations

#### Scenario: Open a violation's file at its line

*Given* checkout-flow's story_map report is open
*When* the Person opens the verb-noun-format violation
*Then* the files panel shows .context/story-map.md with line 6 marked

#### Scenario: Say there is no report

*Given* billing-report has no validation report
*When* the session board reads billing-report
*Then* the story_map bar shows no report link

## Story: Fix Report Violations

#### Scenario: Fix one violation at its line

*Given* checkout-flow's story_map report lists verb-noun-format at .context/story-map.md line 6
*And* a chat is connected
*When* the Person fixes that violation
*Then* the chat's prompt is filled with one message, for the person to edit and send, naming the verb-noun-format rule, the error at .context/story-map.md:6, and the content that failed, with instructions to fix it

#### Scenario: Fix every violation of a rule

*Given* checkout-flow's story_map report lists verb-noun-format
*When* the Person fixes every violation of verb-noun-format
*Then* the chat's prompt is filled with one message, for the person to edit and send: Fix all violations of verb-noun-format found in this report, naming checkout-flow's story_map report

#### Scenario: Fix every violation in the report

*Given* checkout-flow's report lists violations of verb-noun-format and do-not-invent-requirements
*And* a chat is connected
*When* the Person fixes every violation in the report
*Then* the chat's prompt is filled with one message, for the person to edit and send: Fix all violations found in this report, naming checkout-flow's report

#### Scenario: Read an open report again after the fix

*Given* checkout-flow's story_map report is open with verb-noun-format listed
*When* Claude Code validates the story map again with no violations
*Then* the open report lists no rules

## Story: Display Violations Band

#### Scenario: Show the active ticket's violations in a band

*Given* checkout-flow is the active [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) with violations on stories-story-map
*When* the session board reads the board
*Then* a band across the page top names checkout-flow's violations

#### Scenario: Show no band when the active ticket is clean

*Given* billing-report is the active [ticket](../../../../../../space/kanban/.context/kanban-model.md#ticket--card) with no violations
*When* the session board reads the board
*Then* no violations band shows
