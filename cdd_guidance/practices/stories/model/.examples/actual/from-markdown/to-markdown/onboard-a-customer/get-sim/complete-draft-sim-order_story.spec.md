## Story: Complete Draft Sim Order

### Scenario: Complete Draft Sim Order

### Background

*Given* a Customer completed the My Paradise onboarding flow
*And* the Customer's line has ++SIM type++ pSIM
*But* the Customer never entered an ++ICCID++
*And* the ++Mavenir customer++ has ++waiting pSIM++ Active

*Given* Care opens the ++Mavenir customer++ record in Mavenir DEP
*And* Care sees the draft order in the orders grid (`22-dep-orders-grid.png`)
*When* Care attaches the ++ICCID++ to the draft order and completes it
*Then* the order status in DEP Order History changes from draft to active (`23-dep-order-history.png`)
*And* the ++waiting pSIM++ characteristic on the ++Mavenir customer++ is cleared
