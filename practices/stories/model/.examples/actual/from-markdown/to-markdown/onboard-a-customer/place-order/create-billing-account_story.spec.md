## Story: Create Billing Account

### Scenario: Create billing account

### Background

*Given* the Customer has a configured cart
*But* the Customer has no billing account
*When* the Customer creates a billing account
*Then* My Paradise sends the billing account request to Mavenir
*When* Mavenir creates the billing account
*Then* the Customer has a billing account
*And* the Customer is on the Done step


### Scenario: Billing account already exists

### Background

*Given* the Customer has a configured cart
*But* the Customer has no billing account
*When* the Customer creates a billing account
*Then* My Paradise sends the billing account request to Mavenir
*When* Mavenir creates the billing account
*Then* the Customer has a billing account
*And* the Customer is on the Done step
*Given* the Customer has a configured cart
*But* the Customer has no billing account
*Given* the Customer already has a billing account
*When* the Customer creates a billing account
*Then* the billing account is rejected
*And* Mavenir does not receive a billing account request


### Scenario: Billing account creation fails

### Background

*Given* the Customer has a configured cart
*But* the Customer has no billing account
*When* the Customer creates a billing account
*Then* My Paradise sends the billing account request to Mavenir
*When* Mavenir creates the billing account
*Then* the Customer has a billing account
*And* the Customer is on the Done step
*Given* the Customer has a configured cart
*But* the Customer has no billing account
*Given* the Customer already has a billing account
*When* the Customer creates a billing account
*Then* the billing account is rejected
*And* Mavenir does not receive a billing account request
*Given* the Customer has a configured cart
*But* the Customer has no billing account
*Given* Mavenir returns an error for the billing account request
*When* the Customer creates a billing account
*Then* the billing account cannot be created
*And* the Customer has no billing account
