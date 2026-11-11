---
fidelity: [specification]
artifact: [story-scenarios]
format: md
section: body
---

# Sub-epic: Guide Work Through Practices On Board

## Story: Display Fidelity Progress

#### Scenario: Show Generate done

*Given* pet-visits' [session log](../../../../../space/kanban/.context/kanban-model.md#session) has generate /work, /work/docs stories story_map markdown stories
*When* the session board reads pet-visits
*Then* the story_map tile marks Generate ✓ and Validate and Review ○

#### Scenario: Show violations held on Validate

*Given* pet-visits' story_map is generated
*And* its latest validate line is validate Stories story_map graph-rule actor-named-in-step map.md:12
*When* the session board reads pet-visits
*Then* the story_map tile marks Validate as violations and its segment shows in the violations colour
*And* Review stays to do

#### Scenario: Show Validate done after a clean validate

*Given* pet-visits' story_map is generated
*And* its latest validate line is validate Stories story_map with no graph-rule
*When* the session board reads pet-visits
*Then* the story_map tile marks Generate ✓, Validate ✓, and Review ○

#### Scenario: Show each fidelity of the stage on the ticket

*Given* billing-report has nothing recorded in its [session log](../../../../../space/kanban/.context/kanban-model.md#session)
*When* the session board reads billing-report
*Then* each Discovery tile marks Generate, Validate, and Review ○, its segment dim

## Story: Open Practice Tile

#### Scenario: Open a tile on a short hover

*Given* billing-report's card is expanded
*When* the Person rests the pointer on the story_map tile for half a second
*Then* the story_map tile's action bar opens above the grid, at full width
*When* the Person moves the pointer away
*Then* the action bar closes

#### Scenario: Keep a pressed tile open

*Given* billing-report is selected
*When* the Person presses the story_map tile
*Then* the story_map action bar stays open after the pointer leaves
*When* the Person presses the story_map tile again
*Then* the story_map action bar closes

#### Scenario: Keep two pressed tiles open at once

*Given* billing-report's story_map tile is pressed open
*When* the Person presses the bounded_context tile
*Then* both action bars are open
*When* the Person chooses sketch on the bounded_context bar
*Then* only the bounded_context bar's action is sketch

#### Scenario: Open a hovered tile beside a pressed one

*Given* billing-report's card is expanded with the story_map tile pressed open
*When* the Person hovers on the ia tile
*Then* the ia bar opens beside the story_map bar
*When* the Person moves the pointer away from the ia tile
*Then* the ia bar closes and the story_map bar stays open

#### Scenario: Leave a tile in the details closed under a resting pointer

*Given* billing-report is shown in the details
*When* the Person rests the pointer on the story_map tile in the details
*Then* the story_map action bar stays closed

## Story: Choose Ticket Practices

#### Scenario: Turn a practice off for a ticket

*Given* checkout-flow is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) working on every [practice](../../../../../space/kanban/.context/kanban-model.md#practiceguidance)
*And* its bounded_context tile is open
*When* the Person turns DDD off for checkout-flow
*Then* a toast says DDD off for Checkout flow · saved to .sessions/checkout-flow/session.json
*And* the bounded_context tile closes and fades
*And* the card shows no DDD segment

#### Scenario: Finish a stage on the practices left on

*Given* pet-visits has generated, validated, and reviewed the story_map [fidelity](../../../../../space/kanban/.context/kanban-model.md#fidelityguidance)
*And* every practice but Stories is turned off for pet-visits
*When* the session board reads pet-visits
*Then* pet-visits shows in Discovery's Done

#### Scenario: Keep practice switches off on a locked ticket

*Given* Active session only is on
*And* billing-report is not the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card)
*When* the session board draws billing-report's practices
*Then* each practice switch is off until Active session only is turned off

## Story: Send Next Fidelity Action

#### Scenario: Generate the next fidelity in its default format

*Given* billing-report is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) with nothing recorded and a chat is connected
*When* the Person runs billing-report's next step
*Then* Run next read Run next: generate before it ran
*And* the chat receives the command /actions-generate stories-story-map

#### Scenario: Fill the prompt to validate

*Given* back-to-backlog is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) with its story map generated and a chat is connected
*When* the Person runs back-to-backlog's next step
*Then* the chat's prompt holds /actions-validate stories-story-map

#### Scenario: Open the report while violations hold the ticket

*Given* checkout-flow's story map has a verb-noun-format violation on .context/story-map.md line 6
*But* no chat is connected
*When* the Person runs checkout-flow's next step
*Then* Run next read Run next: review violations
*And* the report panel opens on stories-story-map

#### Scenario: Record a review with no chat

*Given* billing-report's story map is generated and validated with no violations
*But* no chat is connected
*When* the Person records a review of billing-report's story_map
*Then* billing-report's story_map marks Review ✓

#### Scenario: Go back to an earlier stage's fidelity still to validate

*Given* pet-visits' story map is generated
*And* a person has moved pet-visits into Specification
*When* the session board reads pet-visits
*Then* Run next reads Run next: validate on stories-story-map

#### Scenario: Keep Run next off where it cannot run

*Given* billing-report is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) with generate next
*But* no chat is connected
*When* the session board draws billing-report's Run next
*Then* Run next is off

#### Scenario: Name nothing to run on a ticket done in its stage

*Given* every Discovery fidelity of pet-visits is reviewed
*When* the session board reads pet-visits
*Then* Run next says Nothing to run next

## Story: Send Action To Stage Practices

#### Scenario: Sketch every fidelity of a stage in one command

*Given* billing-report is the active [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) in Discovery and a chat is connected
*And* the Discovery stage head's action bar is open
*When* the Person runs sketch from the Discovery stage head
*Then* the chat receives the command /actions-sketch stories-story-map ddd-bounded-context ux-ia clean-engineering-modules bdd-behavior

#### Scenario: Keep two stage heads open at once

*Given* billing-report's Discovery stage head is pressed open
*When* the Person presses the Specification stage head
*Then* both stage bars are open

## Story: Mark Ticket Done In Stage

#### Scenario: Mark a ticket done in its stage

*Given* the [ticket](../../../../../space/kanban/.context/kanban-model.md#ticket--card) pet-visits is In progress in Discovery with only its story map generated
*When* the Person marks pet-visits done in Discovery
*Then* pet-visits shows in Discovery's Done
*And* it has no next step
*And* a toast says Pet visits moved to Discovery · Done

#### Scenario: Mark a ticket back in progress

*Given* the ticket ready-to-move is in Discovery's Done
*When* the Person moves ready-to-move back into Discovery's In progress
*Then* ready-to-move shows In progress in Discovery

## Story: Open Help

#### Scenario: Open a fidelity's help

*Given* billing-report's story_map tile is shown
*When* the Person opens help on the story_map fidelity
*Then* a side panel shows story_map's overview, guidance, and rules such as verb-noun-format
*And* it names the stage Discovery
*And* its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/fidelities/stories-story_map.html

#### Scenario: Open a practice's help

*Given* billing-report's [practices](../../../../../space/kanban/.context/kanban-model.md#practiceguidance) are shown in the details
*When* the Person opens help on the Stories practice
*Then* a side panel shows Practice overview and SHARED RULES such as do-not-invent-requirements
*And* it names no fidelity
*And* its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/context-tools/stories.html

#### Scenario: Link the ddd model fidelity to its own page

*Given* the catalog has a page for the ddd model fidelity
*When* the Person opens help on the ddd model fidelity
*Then* its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/fidelities/ddd-model.html
