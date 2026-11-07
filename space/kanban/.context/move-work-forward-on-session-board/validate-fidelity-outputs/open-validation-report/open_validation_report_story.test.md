# (E) Move Work Forward On Session Board
## (E) Validate Fidelity Outputs
### (S) Person --> Open Validation Report

#### Scenario: Open a fidelity's latest report

*Given* checkout-flow's story map has the validation report stories-story-map-20261101T100000.md with its saved graph
*And* the graph names verb-noun-format on .context/story-map.md line 6
*When* the Person opens checkout-flow's story_map report
*Then* the report panel shows .sessions/checkout-flow/validation-reports/stories-story-map-20261101T100000.md
*And* it lists verb-noun-format with one violation at .context/story-map.md line 6 and the source lines around it

#### Scenario: Show every fidelity's violations at once

*Given* checkout-flow has violations
*When* the Person opens checkout-flow's violations from its card
*Then* the report panel shows .sessions/checkout-flow/validation-reports with every rule broken, each naming its fidelity

#### Scenario: Say a report has no saved graph

*Given* the ticket's latest story_map report has no graph saved beside it
*When* the Person opens the story_map report
*Then* the report panel shows the report's text
*And* it says the report has no saved graph in place of saying it has no violations

#### Scenario: Open a violation's file at its line

*Given* checkout-flow's story_map report is open
*When* the Person opens the verb-noun-format violation
*Then* the files panel shows .context/story-map.md with line 6 marked

#### Scenario: Say there is no report

*Given* billing-report has no validation report
*When* the session board reads billing-report
*Then* the story_map bar shows no report link
