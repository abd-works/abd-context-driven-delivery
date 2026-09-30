## Story: Confirm Cognito User

### Scenario: Confirm Cognito User

### Background

*Given* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
*When* Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++
*Then* Cognito confirms the ++Cognito user++
*But* no ++account token++ is issued
*But* no ++Mavenir customer++ exists for those ++account credentials++


### Scenario Outline: Confirm with unusable validation code

### Background

*Given* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
*When* Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++
*Then* Cognito confirms the ++Cognito user++
*But* no ++account token++ is issued
*But* no ++Mavenir customer++ exists for those ++account credentials++
*Given* Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
*When* Cognito is asked to confirm the user with ++validation code++ {scenario}
*Then* Cognito returns {error}
*And* Cognito does not confirm the ++Cognito user++
