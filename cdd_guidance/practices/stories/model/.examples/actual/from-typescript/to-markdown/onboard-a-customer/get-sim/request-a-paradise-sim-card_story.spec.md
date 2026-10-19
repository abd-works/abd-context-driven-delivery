## Story: Request a Paradise Sim Card

### Scenario: Request a Paradise SIM card

*Given* no SIM type is on the line and no ICCID is on the line
*When* the Customer requests a Paradise SIM card
*Then* My Paradise sends the patch cart request to Mavenir with SIM type pSIM
*When* Mavenir returns the updated Mavenir shopping cart with SIM type pSIM
*Then* My Paradise stores pSIM on the line
*But* the line has no ICCID
*And* the Customer is forwarded to Verify ID

### Scenario: Request a Paradise SIM card — already on the line

*Given* the line already has SIM type pSIM
*When* the Customer requests a Paradise SIM card
*Then* My Paradise skips the cart patch

### Scenario: Request a Paradise SIM card — cart patch fails

*Given* Mavenir returns an error on cart patch
*When* the Customer requests a Paradise SIM card
*Then* the SIM selection fails
*When* My Paradise reloads the shopping cart
*Then* the line has no SIM type
*And* the line has no ICCID
