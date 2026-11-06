# (E) Move Work Forward On Session Board
## (E) Generate Fidelity Outputs
### (S) Person --> Generate Fidelity Output

#### Scenario: Send the generate command from a tile

*Given* billing-report is the active [ticket](../../../kanban-model.md#ticket--card) with nothing generated and a chat is connected
*And* its story_map bar has generate chosen and the markdown chip picked
*When* the Person runs generate on story_map
*Then* the chat runs /actions-generate stories-story-map format=markdown
*And* the bar's picks are cleared
*And* Claude Code goes on to Resolve Fidelity Output Paths for stories-story_map

#### Scenario: Render the earlier fidelity into a new format first

*Given* pet-visits' story map is docs/.context/story-map.md, generated in markdown only
*When* the Person generates scenarios in drawio
*Then* the first command is /actions-render stories-story-map format=drawio source=markdown
*And* the last is /actions-generate stories-scenarios format=drawio

#### Scenario: Count a generate line as Generate done

*Given* the [session log](../../../kanban-model.md#session) of pet-visits has no generate line for story_map
*When* Claude Code finishes generating the story map
*Then* the session log ends with a generate line naming stories story_map markdown
*And* the story_map tile marks Generate ✓
