## Story: Choose Esim

### Scenario: Choose eSIM

*Given* no SIM type is on the line
*When* the Customer selects eSIM
*Then* My Paradise sends the patch cart request to Mavenir with SIM type eSIM
*When* Mavenir returns the updated Mavenir shopping cart with SIM type eSIM
*Then* My Paradise stores eSIM on the line
*But* the line has no ICCID
*And* the Customer is forwarded to Verify ID

### Scenario: Choose eSIM — already on the line

*Given* the line already has SIM type eSIM
*When* the Customer selects eSIM
*Then* My Paradise skips the cart patch

### Scenario: Choose eSIM — cart patch fails

*Given* Mavenir returns an error on cart patch
*When* the Customer selects eSIM
*Then* the SIM selection fails
*When* My Paradise reloads the shopping cart
*Then* the line has no SIM type
*And* the line has no ICCID
