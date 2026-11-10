# (E) Move Work Forward On Session Board
## (E) Validate Fidelity Outputs
### (S) Claude Code --> Save Validation Report

#### Scenario: Save the report and the graph it checked

*Given* the [session](../../../kanban-model.md#session) checkout-flow has an entity root with a private-method-naming violation
*When* Claude Code validates ddd-tactics on that file
*Then* the validation report is saved as validation-reports/ddd-tactics-20261101T100000.md naming private-method-naming
*And* the graph it checked is saved beside it as ddd-tactics-20261101T100000.json, with the rule hits on its nodes
*And* Claude Code's reply says where the report is saved

#### Scenario: Save one report for each listed guidance

*Given* the session checkout-flow has edited files for ddd-tactics and stories-scenarios
*When* Claude Code validates ddd-tactics and stories-scenarios together
*Then* validation-reports holds one stories-scenarios report and one ddd-tactics report

#### Scenario: Leave an earlier report's graph as it was

*Given* validation-reports holds ddd-tactics-20200101T000000.json
*When* Claude Code validates ddd-tactics again
*Then* ddd-tactics-20200101T000000.json is unchanged
