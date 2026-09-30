## Story: Submit Reserve Number Request to Mid-Tier

### Scenario: Reserve number

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++available number++ ++chosen available number++ is selected
*But* no ++MSISDN++ is in the ++Mavenir shopping cart++
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++
*Then* Midtier returns 204
*And* My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier


### Scenario: Reserve number — replace existing

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++available number++ ++chosen available number++ is selected
*But* no ++MSISDN++ is in the ++Mavenir shopping cart++
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++
*Then* Midtier returns 204
*And* My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
*And* ++available number++ ++chosen available number++ is selected
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++ with previous ++available number++ ++held available number++
*Then* Midtier returns 204
*And* My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier


### Scenario: Reserve number request fails

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++available number++ ++chosen available number++ is selected
*But* no ++MSISDN++ is in the ++Mavenir shopping cart++
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++
*Then* Midtier returns 204
*And* My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
*And* ++available number++ ++chosen available number++ is selected
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++ with previous ++available number++ ++held available number++
*Then* Midtier returns 204
*And* My Paradise submits a patch cart request with ++available number++ ++chosen available number++ through the Midtier
*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++
*Given* ++available number++ ++chosen available number++ is selected
*When* My Paradise posts a reserve request to Midtier for ++available number++ ++chosen available number++
*But* Midtier returns an error
*Then* My Paradise shows *Failed to reserve your number.*
