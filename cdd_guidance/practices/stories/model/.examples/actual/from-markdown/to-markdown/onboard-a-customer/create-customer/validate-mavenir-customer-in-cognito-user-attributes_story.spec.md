## Story: Validate Mavenir Customer in Cognito User Attributes

### Scenario: Cognito User already has a Mavenir Customer id

### Background

*Given* the User is in Account Setup
*And* Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++

*Given* the ++Cognito user++ has a ++Mavenir customer++ id
*When* the User proceeds to Account Setup
*Then* My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito
*And* My Paradise finds the ++Mavenir customer++ id on the ++Cognito user++
*And* My Paradise proceeds to load the ++My Paradise customer++ from Midtier

### Scenario: Cognito User has no Mavenir Customer id

### Background

*Given* the User is in Account Setup
*And* Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++

*But* no ++Mavenir customer++ exists for those ++account credentials++
*When* the User proceeds to Account Setup
*Then* My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito
*And* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
