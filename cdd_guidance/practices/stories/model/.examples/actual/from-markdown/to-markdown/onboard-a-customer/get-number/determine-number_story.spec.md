## Story: Determine Number

### Examples

#### available number

| available number | example | number | group |
| --- | --- | --- | --- |
| available number | held available number | 4415550100 | available number |
| available number | chosen available number | 4415550101 | available number |

#### search term

| search term | example | input | converted | group |
| --- | --- | --- | --- | --- |
| search term | James search | JAMES | 52637 | search term |

### Scenario: View available numbers

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*But* no ++MSISDN++ is in the ++Mavenir shopping cart++
*When* the Prospect proceeds to selecting their number
*Then* My Paradise loads ++available number++ inventory through the Midtier
*And* the Prospect sees ++available number++ ++held available number++ and ++available number++ ++chosen available number++ in the Available Number list
*And* the Prospect can Bring your mobile number
*And* the Prospect can search for numbers (up to 5 characters: letters or numbers)
*And* the Prospect can Refresh
*And* the Continue operation is disabled
*When* the Prospect selects ++available number++ ++chosen available number++
*Then* the Continue operation is enabled

### Scenario: View available numbers — MSISDN in cart

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
*When* the Prospect proceeds to selecting their number
*Then* the Prospect sees their number is ++available number++ ++held available number++
*And* the Pick new number operation is disabled
*And* the Keep current number operation is enabled
*When* the Prospect selects ++available number++ ++chosen available number++
*Then* the Pick new number operation is enabled

### Scenario: Refresh available numbers

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*When* the Prospect clicks Refresh
*Then* My Paradise loads a fresh set of ++available number++ through the Midtier
*And* the Prospect sees a new Available Number list
*And* the Continue operation is disabled

### Scenario: Search for a number

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*When* the Prospect enters ++search term++ ++James search++ in the search field
*Then* the search field helper shows *Your number: JAMES (52637)*
*When* the Prospect triggers the search
*Then* My Paradise loads Available Numbers matching ++search term++ ++James search++ through the Midtier
