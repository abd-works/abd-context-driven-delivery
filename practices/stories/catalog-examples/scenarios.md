---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Determine Number

#### Examples

##### available number

| available number | example | number |
| --- | --- | --- |
| available number | held available number | 4415550100 |
| available number | chosen available number | 4415550101 |
| available number | James matching numbers | 5263712345, 5263798765 |
| available number | numbers locked by another customer | 4415550200, 4415550201 |

##### search term

| search term | example | input | converted |
| --- | --- | --- | --- |
| search term | James search | JAMES | 52637 |

##### Mavenir shopping cart

| Mavenir shopping cart | example | id | customer | bundle | MSISDN |
| --- | --- | --- | --- | --- | --- |
| Mavenir shopping cart | empty cart | cart_cus_1 | cus_1 | | |
| Mavenir shopping cart | cart holding held available number | cart_cus_1 | cus_1 | plan_1 | 4415550100 |

##### account credentials

| account credentials | example | email | password | confirmPassword |
| --- | --- | --- | --- | --- |
| account credentials | valid account credentials | prospect@example.com | Valid-pass99 | Valid-pass99 |

#### Background

*Given* a ++My Paradise customer++ with a ++Mavenir shopping cart++

#### Scenario: View available numbers

*But* no ++MSISDN++ is in the ++Mavenir shopping cart++
  *And* ++available number++ ++held available number++ and ++available number++ ++chosen available number++ are available in Mavenir
*When* the Customer loads available numbers
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir locks 20 MSISDN resources and returns the available number values
*Then* My Paradise returns the available numbers
  *And* ++available number++ ++held available number++ and ++available number++ ++chosen available number++ are in the Available Number list

#### Scenario: View available numbers — MSISDN in cart

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
  *And* ++available number++ ++held available number++ and ++available number++ ++chosen available number++ are available in Mavenir
*When* the Customer loads available numbers
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir locks 20 MSISDN resources and returns the available number values
*Then* the Customer sees their number is ++available number++ ++held available number++
  *And* My Paradise returns the available numbers

#### Scenario: Refresh available numbers

*Given* ++available number++ ++held available number++ and ++available number++ ++chosen available number++ are available in Mavenir
*When* the Customer refreshes the number list
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir locks 20 MSISDN resources and returns the available numbers
*Then* My Paradise returns a fresh set of available numbers

#### Scenario: Search for a number

*Given* ++available number++ ++James matching numbers++ are available in Mavenir
*When* the Customer searches for numbers matching ++search term++ ++James search++
*Then* My Paradise sends the search request to Mavenir with pattern ++search term++ ++James search++
*When* Mavenir locks MSISDN resources matching 52637 and returns matching values
*Then* My Paradise returns Available Numbers matching 52637
  *And* the matching numbers are stored on the line for selection

#### Scenario: Numbers locked by another customer are excluded from results

*Given* another customer has already locked ++available number++ ++held available number++ and ++available number++ ++chosen available number++ in Mavenir
  *And* ++available number++ ++numbers locked by another customer++ are the currently available numbers
*When* the Customer loads available numbers
*Then* My Paradise sends the list resources request to Mavenir
*When* Mavenir returns only available numbers, excluding the locked ones
*Then* the locked numbers are not in the available numbers list
  *And* only the currently available numbers are returned
