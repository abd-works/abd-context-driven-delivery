# (E) Move Work Forward On Session Board
## (E) Guide Work Through Practices
### (S) Person --> Open Help

#### Scenario: Open a fidelity's help

*Given* billing-report's story_map tile is shown
*When* the Person opens help on the story_map fidelity
*Then* a side panel shows story_map's overview, guidance, and rules such as verb-noun-format
*And* it names the stage Discovery
*And* its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/fidelities/stories-story_map.html

#### Scenario: Open a practice's help

*Given* billing-report's [practices](../../../kanban-model.md#practiceguidance) are shown in the details
*When* the Person opens help on the Stories practice
*Then* a side panel shows Practice overview and SHARED RULES such as do-not-invent-requirements
*And* it names no fidelity
*And* its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/context-tools/stories.html

#### Scenario: Link the ddd model fidelity to its own page

*Given* the catalog has a page for the ddd model fidelity
*When* the Person opens help on the ddd model fidelity
*Then* its Forge link opens https://forge.abdworks.net/abd-context-driven-delivery/fidelities/ddd-model.html
