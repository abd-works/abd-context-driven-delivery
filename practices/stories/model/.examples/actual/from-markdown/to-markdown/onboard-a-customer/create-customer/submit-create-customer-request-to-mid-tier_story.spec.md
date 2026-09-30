## Story: Submit Create Customer Request to Mid-Tier

### Scenario: Submit Create Customer Request to Mid-Tier

### Background

*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise adds a ++Mavenir customer++ through the Midtier


### Scenario: Email already has a Mavenir Customer

### Background

*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise adds a ++Mavenir customer++ through the Midtier
*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*Given* a ++Mavenir customer++ already exists for that email
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise shows *Could not create customer.*


### Scenario: Invalid Account Token

### Background

*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise adds a ++Mavenir customer++ through the Midtier
*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*Given* a ++Mavenir customer++ already exists for that email
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise shows *Could not create customer.*
*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*Given* the ++account token++ is invalid
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise shows *Could not create customer.*


### Scenario: Mavenir is unreachable

### Background

*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise adds a ++Mavenir customer++ through the Midtier
*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*Given* a ++Mavenir customer++ already exists for that email
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise shows *Could not create customer.*
*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*Given* the ++account token++ is invalid
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise shows *Could not create customer.*
*Given* the ++Cognito user++ has no ++Mavenir customer++ id
*And* the browser session has an ++account token++
*Given* Mavenir has no HTTP response
*When* My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++
*Then* My Paradise shows *Could not create customer.*
