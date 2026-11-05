# (E) Move Work Forward On Session Board
## (E) Generate Fidelity Outputs
### (S) Person --> Render Fidelity Format

#### Scenario: Render existing output into another format

*Given* billing-report's story map is tests/story-map.md, in markdown
*And* a chat is connected
*When* the Person renders story_map into the diagram format
*Then* the chat receives the command /actions-render stories-story-map format=drawio

#### Scenario: Keep render off with nothing to render

*Given* billing-report's story map has no file
*When* the Person chooses render on the story_map bar
*Then* Run is off
