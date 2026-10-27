## Story: Load My Paradise Customer From Midtier And Store In Session

### Story Background: each

*Given* Mavenir has a customer and the Cognito user holds its id

### Scenario: Load My Paradise Customer From Midtier And Store In Session

*When* My Paradise loads the customer through Midtier
*Then* My Paradise calls Midtier with the correct customer id
*And* Midtier maps the Mavenir contact medium to Paradise identity and address

### Examples

| example |
| --- |
| enteredValidAccountCredentials |

### Scenario: Load customer fails

*Given* Mavenir no longer has that customer
*When* My Paradise loads the customer
*Then* My Paradise signs the User out
*And* My Paradise shows Something went wrong when loading your account

### Scenario: Terminated account

*Given* the Customer has an account token
*And* the Mavenir customer billing state is terminated
*When* My Paradise loads the customer
*Then* My Paradise signs the Customer out
*And* the Customer account is terminated

### Examples

| example |
| --- |
| storedAccountCredentialsWithToken |
