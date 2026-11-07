# (E) Move Work Forward On Session Board
## (E) Guide Work Through Practices
### (S) Board App --> Display Fidelity Progress

#### Scenario: Show Generate done

*Given* pet-visits' [session log](../../../kanban-model.md#session) has generate /work, /work/docs stories story_map markdown stories
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

*Given* billing-report has nothing recorded in its [session log](../../../kanban-model.md#session)
*When* the session board reads billing-report
*Then* each Discovery tile marks Generate, Validate, and Review ○, its segment dim
