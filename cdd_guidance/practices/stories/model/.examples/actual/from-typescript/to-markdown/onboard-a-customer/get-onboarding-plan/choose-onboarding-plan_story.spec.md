## Story: Choose Onboarding Plan

### Scenario: Select a plan

*Given* no plan is in the Mavenir shopping cart
*When* the Customer selects Essentials
*Then* My Paradise patches the Mavenir cart with the Essentials planId
*And* the Customer is forwarded to Pick Number
*When* Mavenir confirms the cart is patched with Essentials
*Then* the cart bundle is a snapshot of Essentials loaded from the gateway

### Scenario: Change an existing plan

*Given* Essentials is in the Mavenir shopping cart
*When* the Customer selects Data Freedom
*Then* My Paradise patches the Mavenir cart with the Data Freedom planId
*When* Mavenir confirms the cart is patched with Data Freedom
*Then* the cart bundle is updated to a snapshot of Data Freedom loaded from the gateway

### Scenario: Failed to update plan

*Given* the Mavenir cart patch returns an error
*When* the Customer selects Essentials
*Then* the plan selection fails
*When* My Paradise reloads the shopping cart
*Then* the cart bundle remains empty
