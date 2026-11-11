# (E) Move Work Forward On Session Board
## (E) Guide Work Through Practices
### (S) Person --> Send Next Fidelity Action

#### Scenario: Generate the next fidelity in its default format

*Given* billing-report is the active [ticket](../../../kanban-model.md#ticket--card) with nothing recorded and a chat is connected
*When* the Person runs billing-report's next step
*Then* Run next read Run next: generate before it ran
*And* the chat receives the command /actions-generate stories-story-map

#### Scenario: Fill the prompt to validate

*Given* back-to-backlog is the active [ticket](../../../kanban-model.md#ticket--card) with its story map generated and a chat is connected
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

*Given* billing-report is the active [ticket](../../../kanban-model.md#ticket--card) with generate next
*But* no chat is connected
*When* the session board draws billing-report's Run next
*Then* Run next is off

#### Scenario: Name nothing to run on a ticket done in its stage

*Given* every Discovery fidelity of pet-visits is reviewed
*When* the session board reads pet-visits
*Then* Run next says Nothing to run next
