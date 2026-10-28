## Story: Create Order Ticket

### Scenario: Create order ticket: ${example}

*Given* the Customer ${example}
*When* the Customer creates the order ticket
*Then* My Paradise sends the ${subject} ticket to Zendesk
*When* Zendesk creates the ticket
*Then* the ticket is created for the Customer

### Examples

| example |
| --- |
| customerReadyToPlaceOrder |
| expectedTicketRequest |
| requesterName |
