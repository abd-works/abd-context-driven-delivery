## Story: Enter Payment

### Scenario: Enter Payment

*Given* the Customer is at Checkout with Essentials
*And* Mavenir CCS authorizes stub auth
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir with TotalAmount $1 and salesChannel ON-BOARDING
*When* Mavenir authorizes the card and returns the hosted payment page
*Then* the payment has stub auth transaction id, amount $1, and sales channel ON-BOARDING

### Scenario: Payment authorization fails to load

*Given* the Customer is at Checkout with Essentials
*But* Mavenir CCS does not return a payment authorization
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a payment authorization
*Then* the payment authorization cannot be loaded

### Scenario: FAC authorization timeout

*Given* the Customer is at Checkout with Essentials
*But* Mavenir does not return a transaction id
*When* the Customer proceeds to adding their payment
*Then* My Paradise sends the card authorization request to Mavenir
*When* Mavenir does not return a transaction id
*Then* the payment authorization cannot be loaded
