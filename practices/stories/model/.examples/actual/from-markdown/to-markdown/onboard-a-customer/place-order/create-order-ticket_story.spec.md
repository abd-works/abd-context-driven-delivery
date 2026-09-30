## Story: Create Order Ticket

### Scenario Outline: Create order ticket

*Given* the Customer {example}
*When* the Customer creates the order ticket
*Then* My Paradise sends the {subject} ticket to Zendesk
*When* Zendesk creates the ticket
*Then* the ticket is created for the Customer
