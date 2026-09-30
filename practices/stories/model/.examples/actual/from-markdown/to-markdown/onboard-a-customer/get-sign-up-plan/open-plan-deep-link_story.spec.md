## Story: Open Plan Deep Link

### Scenario Outline: Open Plan Deep Link

### Background

*Given* the plan catalog contains purchasable plans
*And* the Customer arrived at sign-up from the Paradise Mobile website
*When* the Customer opens a plan deep link for ++plan++ ++{scenario}++
*Then* ++{scenario}++ is selected
*And* the Customer continues to Enter Account Credentials


### Scenario: Unknown plan deep link

### Background

*Given* the plan catalog contains purchasable plans
*And* the Customer arrived at sign-up from the Paradise Mobile website
*When* the Customer opens a plan deep link for ++plan++ ++{scenario}++
*Then* ++{scenario}++ is selected
*And* the Customer continues to Enter Account Credentials
*Given* the plan catalog contains purchasable plans
*And* the Customer arrived at sign-up from the Paradise Mobile website
*Given* the plan catalog contains purchasable plans
*But* the deep-link plan id is not in the catalog
*When* the Customer opens a plan deep link
*Then* the plan is not found
