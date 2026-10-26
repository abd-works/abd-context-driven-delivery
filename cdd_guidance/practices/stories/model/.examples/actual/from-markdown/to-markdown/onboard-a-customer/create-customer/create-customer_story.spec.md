## Story: Create Customer

### Scenario: Create Customer

### Background

*Given* no ++Mavenir customer++ for that email
*And* Mavenir has that ++account token++ on the create request

*When* Mavenir is asked to create a ++Mavenir customer++ for that email
*Then* Mavenir creates a ++Mavenir customer++
*And* Mavenir returns the ++Mavenir customer++ id

### Scenario: Email already has a Mavenir Customer

### Background

*Given* no ++Mavenir customer++ for that email
*And* Mavenir has that ++account token++ on the create request

*Given* Mavenir has a ++Mavenir customer++ for that email
*When* Mavenir is asked to create a ++Mavenir customer++ for that email
*Then* Mavenir returns a conflict
