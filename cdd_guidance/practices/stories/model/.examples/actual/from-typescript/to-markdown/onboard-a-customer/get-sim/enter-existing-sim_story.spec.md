## Story: Enter Existing Sim

### Scenario: Enter existing SIM

*Given* Mavenir has valid ICCID available in inventory
*When* the Customer attaches valid ICCID
*Then* My Paradise sends the ICCID inventory request to Mavenir with valid ICCID
*And* My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID
*When* Mavenir returns the updated Mavenir shopping cart with SIM type pSIM and valid ICCID
*Then* My Paradise stores pSIM and valid ICCID on the line
*And* the line has valid ICCID
*And* the Customer is forwarded to Verify ID

### Scenario: ICCID contains spaces

*Given* the Customer has ICCID with spaces
*When* the Customer attaches ICCID with spaces
*Then* the ICCID format is rejected
*And* My Paradise does not query inventory or patch the cart

### Scenario: Inventory rejects ICCID

*Given* Mavenir does not have invalid ICCID available in inventory
*When* the Customer attaches invalid ICCID
*Then* My Paradise sends the ICCID inventory request to Mavenir with invalid ICCID
*And* My Paradise does not patch the cart
*And* the ICCID is rejected
