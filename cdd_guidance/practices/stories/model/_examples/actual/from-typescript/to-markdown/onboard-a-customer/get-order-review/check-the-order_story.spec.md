## Story: Check The Order

### Scenario: Check the order: ${example}

*Given* the Customer has completed account setup, number, SIM, and profile
*When* My Paradise loads the order state from the Mavenir shopping cart
*Then* the Customer is forwarded to Checkout
*And* the order summary shows the plan
*And* the order summary shows the number and SIM
*And* the order summary shows the profile

### Examples

| example |
| --- |
| seedCustomerCart |
| loadCart |
| stubBundle |
