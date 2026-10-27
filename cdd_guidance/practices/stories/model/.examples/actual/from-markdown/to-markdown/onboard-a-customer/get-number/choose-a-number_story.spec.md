## Story: Choose a Number

### Scenario: Pick new number

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* the Prospect has selected ++available number++ ++chosen available number++
*But* no ++MSISDN++ is in the ++Mavenir shopping cart++
*When* the Prospect clicks Continue
*Then* My Paradise reserves ++available number++ ++chosen available number++ through the Midtier
*And* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
*And* the Prospect is forwarded to Select Sim

### Scenario: Pick new number — replace existing

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
*And* the Prospect has selected ++available number++ ++chosen available number++
*When* the Prospect clicks Pick new number
*Then* My Paradise reserves ++available number++ ++chosen available number++ releasing ++available number++ ++held available number++ through the Midtier
*And* My Paradise patches the ++Mavenir shopping cart++ with ++available number++ ++chosen available number++ through the Midtier
*And* the Prospect is forwarded to Select Sim

### Scenario: Keep current number

### Background

*Given* the Prospect is in Account Setup
*And* a ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* ++MSISDN++ ++available number++ ++held available number++ is in the ++Mavenir shopping cart++
*When* the Prospect clicks Keep current number
*Then* the Prospect is forwarded to Select Sim
