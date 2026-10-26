## Story: Create Product Order

### Scenario: Create product order

*Given* the Customer is verified and has a billing account, plan, number, and eSIM
*When* the Customer places the product order
*Then* My Paradise sends the product order request to Mavenir
*When* Mavenir creates the product order
*Then* the order succeeded with pay-up-front
*And* the Customer onboarding is done

### Scenario: Pay-up-front charge fails

*Given* the pay-up-front charge fails
*When* the Customer places the product order
*Then* My Paradise does not send a product order to Mavenir
*When* My Paradise reloads the cart
*Then* the order succeeded without pay-up-front

### Scenario: Product order fails

*Given* Mavenir returns an error for the product order
*When* the Customer places the product order
*Then* My Paradise sends the product order request to Mavenir
*When* My Paradise reloads the cart
*Then* the order did not succeed

### Scenario: Onboarding is already done

*Given* the Customer onboarding is already done
*When* the Customer places the product order
*Then* the product order is rejected
*And* Mavenir does not receive a product order request

### Scenario: Unverified with no bypass and no portability

*Given* the Customer is not verified and the plan does not bypass verification
*When* the Customer places the product order
*Then* My Paradise does not send a product order to Mavenir
*And* the cart is marked to submit the order later
*When* My Paradise reloads the cart
*Then* the Customer onboarding is done
