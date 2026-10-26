## Story: Issue Account Token To Browser Session

### Scenario: Issue Account Token To Browser Session

### Background

*Given* Cognito has a ++Cognito user++ ++confirmed Cognito user++

*When* Cognito is asked to authenticate ++account credentials++ ++valid account credentials++
*Then* Cognito issues an ++account token++ for the ++Cognito user++
*But* no ++Mavenir customer++ exists for those ++account credentials++
