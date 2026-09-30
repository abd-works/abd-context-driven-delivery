## Story: Create Unconfirmed Cognito User

### Scenario: Create Unconfirmed Cognito User

### Background

*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
*When* Cognito is asked to register ++account credentials++ ++valid account credentials++
*Then* Cognito creates ++Cognito user++ ++unconfirmed Cognito user++
*And* Cognito emails a ++validation code++ for those ++account credentials++
*But* no ++account token++ is issued
*But* no ++Mavenir customer++ exists for those ++account credentials++


### Scenario: Email already registered in Cognito

### Background

*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
*When* Cognito is asked to register ++account credentials++ ++valid account credentials++
*Then* Cognito creates ++Cognito user++ ++unconfirmed Cognito user++
*And* Cognito emails a ++validation code++ for those ++account credentials++
*But* no ++account token++ is issued
*But* no ++Mavenir customer++ exists for those ++account credentials++
*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
*Given* ++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++
*When* Cognito is asked to register ++account credentials++ ++already-registered account credentials++
*Then* Cognito returns ++UsernameExistsException++
*And* Cognito does not create another ++Cognito user++ for those ++account credentials++


### Scenario: Cognito register fails with another error

### Background

*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
*When* Cognito is asked to register ++account credentials++ ++valid account credentials++
*Then* Cognito creates ++Cognito user++ ++unconfirmed Cognito user++
*And* Cognito emails a ++validation code++ for those ++account credentials++
*But* no ++account token++ is issued
*But* no ++Mavenir customer++ exists for those ++account credentials++
*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
*Given* ++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++
*When* Cognito is asked to register ++account credentials++ ++already-registered account credentials++
*Then* Cognito returns ++UsernameExistsException++
*And* Cognito does not create another ++Cognito user++ for those ++account credentials++
*Given* no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
