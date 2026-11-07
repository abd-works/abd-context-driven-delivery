# (E) Move Work Forward On Session Board
## (E) Review Fidelity Outputs
### (S) Person --> Review Fidelity

#### Scenario: Review a fidelity after a clean validate

*Given* billing-report's story map is generated and its latest validate passed with no graph-rule
*When* the Person reviews story_map on billing-report
*Then* billing-report's session log ends with review Stories story_map
*And* the story_map tile marks Review ✓ and the fidelity is done
*And* a toast says stories-story-map done on billing-report

#### Scenario: Keep Review off until Validate is clean

*Given* billing-report's story map has no file
*But* nothing is recorded on it
*When* the session board draws the story_map bar
*Then* review is off

#### Scenario: Ignore a review recorded before a clean validate

*Given* pet-visits' session log has generate, then review, then validate Stories story_map
*When* the session board reads pet-visits
*Then* the story_map tile marks Review ○

#### Scenario: Refuse a fidelity the ticket does not have

*Given* billing-report's story map passed validate
*When* the Person reviews stories-no_such_fidelity
*Then* the board says no fidelity named stories-no_such_fidelity on ticket billing-report
*But* no review line is written for stories-story-map

#### Scenario: Complete a stage's work

*Given* pet-visits has every Discovery fidelity generated, validated, and reviewed
*When* the session board reads pet-visits
*Then* pet-visits waits in Discovery's Done
*And* it has no next step
