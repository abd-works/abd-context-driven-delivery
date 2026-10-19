## Story: Create Customer

### Story Background: each

*Given* the User has a verified account with an account token

### Scenario: Create customer

*When* the User creates their Paradise account
*Then* My Paradise sends the correct create request to Mavenir
*When* Mavenir creates the customer
*Then* the customer has a Mavenir customer id
*And* My Paradise stores the customer id on the Cognito user

### Examples

| example |
| --- |
| enteredValidAccountCredentials |

### Scenario: Mavenir customer already exists

*Given* Mavenir already has a customer for that email
*When* the User creates their Paradise account
*Then* My Paradise shows Could not create customer

### Examples

| example |
| --- |
| enteredValidAccountCredentials |
