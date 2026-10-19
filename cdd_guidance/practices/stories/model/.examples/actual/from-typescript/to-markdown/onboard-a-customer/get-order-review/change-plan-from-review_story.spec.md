## Story: Change Plan From Review

### Scenario: Select a different plan from review

*Given* the Customer has opened plan selection from review with Essentials in the cart
*When* My Paradise patches the Mavenir shopping cart with Data Freedom
*Then* My Paradise sends the patch cart request to Mavenir with Data Freedom bundleId
*When* Mavenir returns the updated Mavenir shopping cart with Data Freedom
*Then* My Paradise stores Data Freedom as the cart bundle loaded from the gateway
*And* the Customer is forwarded to Checkout

### Scenario: Keep current plan from review

*Given* the Customer has opened plan selection from review with Essentials in the cart
*When* the Customer keeps their current plan
*Then* the cart bundle remains Essentials
*And* the Customer is forwarded to Checkout

### Scenario: Plan update fails from review

*Given* the Customer has opened plan selection from review with Essentials in the cart
*When* My Paradise patches the Mavenir shopping cart with Data Freedom but Mavenir returns an error
*Then* My Paradise shows Failed to update new plan choice.
*When* My Paradise reloads the shopping cart
*Then* the cart bundle remains Essentials
