## Story: Open Plan Deep Link

### Scenario: Open plan deep link: ${plan.name}

*Given* the plan catalog contains purchasable plans and the Customer arrived at sign-up from the Paradise Mobile website
*When* the Customer opens a plan deep link for ${plan.name}
*Then* ${plan.name} is selected
*And* the Customer continues to Enter Account Credentials

### Examples

| example |
| --- |
| seedPurchasableCatalog |

### Scenario: Unknown plan deep link

*Given* the plan catalog contains purchasable plans
*But* the deep-link plan id is not in the catalog
*When* the Customer opens a plan deep link
*Then* the plan is not found

### Examples

| example |
| --- |
| seedPurchasableCatalog |
| unknownPlanDeepLinkId |
