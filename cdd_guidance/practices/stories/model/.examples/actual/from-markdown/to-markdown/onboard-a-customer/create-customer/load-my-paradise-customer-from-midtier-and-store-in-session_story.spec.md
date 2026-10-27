## Story: Load My Paradise Customer From Midtier And Store In Session

### Scenario: Load My Paradise Customer From Midtier And Store In Session

### Background

*Given* the browser session has an ++account token++
*And* the ++Cognito user++ has a ++Mavenir customer++ id
*And* the ++My Paradise customer++ is not in session

*When* the User proceeds to Account Setup or My Paradise
*Then* My Paradise retrieves the ++Mavenir customer++ through the Midtier
*And* My Paradise stores the ++My Paradise customer++ in session

### Scenario: Billing account is terminated

### Background

*Given* the browser session has an ++account token++
*And* the ++Cognito user++ has a ++Mavenir customer++ id
*And* the ++My Paradise customer++ is not in session

*Given* the ++Mavenir customer++ billing state is terminated
*When* the User proceeds to Account Setup or My Paradise
*Then* My Paradise signs the User out
*And* My Paradise shows the terminated-account message

### Scenario: Load customer fails

### Background

*Given* the browser session has an ++account token++
*And* the ++Cognito user++ has a ++Mavenir customer++ id
*And* the ++My Paradise customer++ is not in session

*When* the User proceeds to Account Setup or My Paradise
*Then* My Paradise signs the User out
*And* My Paradise shows *Something went wrong when loading your account*
