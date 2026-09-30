## Story: Store Mavenir Customer Id on Cognito User

### Scenario: Store Mavenir Customer Id on Cognito User

### Background

*Given* My Paradise has added a ++Mavenir customer++ through the Midtier
*And* that add returned a ++Mavenir customer++ id
*When* My Paradise has a ++Mavenir customer++ id from the Midtier
*Then* My Paradise stores the ++Mavenir customer++ id on the ++Cognito user++ routing through Amplify to Cognito
*And* My Paradise proceeds to load the ++My Paradise customer++ from Midtier
