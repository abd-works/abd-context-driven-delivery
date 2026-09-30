## Story: Check The Order

### Scenario: Check the order

### Background

*Given* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*And* ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
*And* the Customer has chosen eSIM
*Given* the Customer has completed account setup, number, SIM, and profile
*When* the Customer proceeds to reviewing their order
*Then* the Customer is forwarded to Checkout
*And* the Checkout step is the next onboarding step


### Scenario: Check the order with port-in number

### Background

*Given* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*And* ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
*And* the Customer has chosen eSIM
*Given* the Customer has completed account setup, number, SIM, and profile
*When* the Customer proceeds to reviewing their order
*Then* the Customer is forwarded to Checkout
*And* the Checkout step is the next onboarding step
*Given* the Customer has a ++My Paradise customer++ with ++plan++ ++Essentials++ in the ++Mavenir shopping cart++
*And* ++available number++ ++chosen available number++ is in the ++Mavenir shopping cart++
*And* the Customer has chosen eSIM
*Given* the Customer has a port-in number with +1 (441) 123-4567 as port number and +1 (441) 555-0101 as temporary MSISDN
*When* the Customer proceeds to reviewing their order
*Then* the Customer is forwarded to Checkout
*And* the Checkout step is the next onboarding step
