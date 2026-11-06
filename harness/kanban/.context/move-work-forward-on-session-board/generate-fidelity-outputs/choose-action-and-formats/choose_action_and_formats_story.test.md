# (E) Move Work Forward On Session Board
## (E) Generate Fidelity Outputs
### (S) Person --> Choose Action And Formats

#### Scenario: Pick the fidelity's default format

*Given* billing-report's story_map [fidelity](../../../kanban-model.md#fidelityguidance) has no file generated
*When* the Person opens the story_map tile
*Then* the generate action is chosen with the markdown chip picked

#### Scenario: Leave a generated format unpicked

*Given* billing-report's story map is .context/story-map.md, already there
*When* the Person opens the story_map tile
*Then* the markdown chip is green and not picked

#### Scenario: Stand one chip for a group of formats

*Given* billing-report's story map is generated in markdown and its bounded context is not
*When* the Person opens the Discovery stage head on story_map and bounded_context
*Then* the bar shows a diagram chip and a markdown chip
*And* the markdown chip reads 1 of 2 with the hint markdown: 1 of 2 done

#### Scenario: Keep Run off with no format picked

*Given* billing-report's story map is already in markdown
*But* no format is picked
*When* the session board draws the story_map bar
*Then* Run is off

#### Scenario: Keep Run off on a render with nothing to render

*Given* billing-report's story map has no file
*When* the Person chooses render on the story_map bar
*Then* Run is off

#### Scenario: Keep Run off with no chat

*Given* the story_map bar has the markdown chip picked
*But* no chat is connected
*When* the session board draws the story_map bar
*Then* Run is off

#### Scenario: Keep Run off on a locked ticket

*Given* Active session only is on
*And* billing-report is not the active [ticket](../../../kanban-model.md#ticket--card)
*And* billing-report's story_map bar has the markdown chip picked
*When* the session board draws billing-report's story_map bar
*Then* Run is off
