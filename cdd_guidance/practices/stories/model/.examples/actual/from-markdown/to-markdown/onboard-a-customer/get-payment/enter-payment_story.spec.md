## Story: Enter Payment

### Examples

#### payment authorization

| payment authorization | example | transactionId | totalAmount | salesChannel | group |
| --- | --- | --- | --- | --- | --- |
| payment authorization | stub auth | d4a1b2c3-9f3a-4e1b-8c7d-a2b5e8f1d0c3 | 1 | ON-BOARDING | payment authorization |

### Scenario: Enter Payment

### Background

*Given* the Customer has completed order review and is on Checkout
*And* the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* `payUpFront` is off
*And* Mavenir CCS authorizes ++payment authorization++ ++stub auth++
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
*When* Mavenir authorizes the card and returns the hosted payment page
*Then* My Paradise stores ++payment authorization++ ++stub auth++

### Scenario: Pay upfront

### Background

*Given* the Customer has completed order review and is on Checkout
*And* the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* `payUpFront` is on
*And* the cart has ++plan++ ++Essentials++
*And* Mavenir CCS authorizes ++payment authorization++ ++stub auth++
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
*When* Mavenir authorizes the card and returns the hosted payment page
*Then* My Paradise stores ++payment authorization++ ++stub auth++

### Scenario: Payment authorization fails to load

### Background

*Given* the Customer has completed order review and is on Checkout
*And* the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* `payUpFront` is off
*But* Mavenir CCS does not return a payment authorization
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a payment authorization
*Then* the payment authorization cannot be loaded

### Scenario: FAC authorization timeout

### Background

*Given* the Customer has completed order review and is on Checkout
*And* the Customer has a loaded ++My Paradise customer++ with a ++Mavenir shopping cart++

*Given* `payUpFront` is off
*But* Mavenir does not return a transaction id
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a transaction id
*Then* the payment authorization cannot be loaded
