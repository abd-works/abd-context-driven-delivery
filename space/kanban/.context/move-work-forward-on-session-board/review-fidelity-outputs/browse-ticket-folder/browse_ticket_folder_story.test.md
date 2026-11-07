# (E) Move Work Forward On Session Board
## (E) Review Fidelity Outputs
### (S) Person --> Browse Ticket Folder

#### Scenario: Group a stage's files under their folders

*Given* checkout-flow's Discovery files are tests/a.md, tests/deep/b.md, and src/c.ts
*When* the Person browses checkout-flow's Discovery files
*Then* the files panel groups a.md and deep/b.md under tests/ and c.ts under src/

#### Scenario: Browse the ticket's session folder

*Given* checkout-flow's [session](../../../kanban-model.md#session) folder holds its log and validation-reports/stories-story-map-20261101T100000.md
*When* the Person browses checkout-flow's session folder
*Then* the files panel lists .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md under its folder
