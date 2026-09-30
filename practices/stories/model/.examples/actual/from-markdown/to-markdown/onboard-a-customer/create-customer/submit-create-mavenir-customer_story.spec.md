## Story: Submit Create Mavenir Customer

### Scenario: Submit Create Mavenir Customer

### Background

*Given* Midtier has verified the ++account token++
*And* the ++account token++ has an email

*When* Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++
*Then* Midtier maps that request to a Mavenir createaccounts for a ++Mavenir customer++ (email and ++contact medium++ from that email)
*And* Midtier submits createaccounts to Mavenir
*And* Midtier receives a Mavenir createaccounts response with the ++Mavenir customer++ id
*And* Midtier maps that ++Mavenir customer++ id to a ++PML customer++ id
*And* Midtier returns the ++PML customer++ id

### Scenario: Mavenir customer already exists

### Background

*Given* Midtier has verified the ++account token++
*And* the ++account token++ has an email

*Given* a ++Mavenir customer++ already exists for that email
*When* Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++
*Then* Midtier receives a Mavenir createaccounts conflict
*And* Midtier maps that conflict to Paradise 409
*And* Midtier returns 409

### Scenario: Mavenir is unreachable

### Background

*Given* Midtier has verified the ++account token++
*And* the ++account token++ has an email

*Given* Mavenir has no HTTP response
*When* Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++
*Then* Midtier maps that missing response to Paradise 504
*And* Midtier returns 504
