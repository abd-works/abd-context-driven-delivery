## Story: Open Plan Deep Link

### Scenario: Unknown plan deep link

*Given* the plan catalog contains purchasable plans
*But* the deep-link plan id is not in the catalog
*When* the Customer opens a plan deep link
*Then* the plan is not found
