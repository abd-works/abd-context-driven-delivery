## Story: Create Product Order

### Scenario: Create product order

### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* the Customer is verified
*When* the Customer places the product order
*Then* My Paradise sends the product order request to Mavenir
*When* Mavenir creates the product order
*Then* the order succeeded with pay-up-front
*And* the Customer onboarding is done

### Scenario: Pay-up-front charge fails

### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* the pay-up-front charge fails
*When* the Customer places the product order
*Then* My Paradise does not send a product order to Mavenir
*And* the order succeeded without pay-up-front

### Scenario: Product order fails

### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* Mavenir returns an error for the product order
*When* the Customer places the product order
*Then* the order did not succeed

### Scenario: Onboarding is already done

### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* the Customer onboarding is already done
*When* the Customer places the product order
*Then* the product order is rejected
*And* Mavenir does not receive a product order request

### Scenario: Unverified with no bypass and no portability

### Background

*Given* the Customer has a billing account
*And* the cart has plan, number, and SIM

*Given* the Customer is not verified
*And* the plan does not bypass verification
*And* the cart has no portability
*When* the Customer places the product order
*Then* My Paradise does not send a product order to Mavenir
*And* the cart is marked to submit the order later
*And* the Customer onboarding is done
