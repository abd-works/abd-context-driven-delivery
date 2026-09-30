## Story: Validate Cognito User

### Scenario: Validate Cognito User

### Background

*Given* the User has an ++account token++
*When* Midtier is asked to validate the ++account token++
*Then* Midtier verifies the ++account token++
*And* Midtier reads the email from the ++account token++
*When* the ++account token++ is invalid
*Then* Midtier returns "Invalid token"
