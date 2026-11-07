# (E) Move Work Forward On Session Board
## (E) Validate Fidelity Outputs
### (S) Person --> Validate Fidelity

#### Scenario: Send the fidelity to validate

*Given* billing-report is the active [ticket](../../../kanban-model.md#ticket--card) and a chat is connected
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
