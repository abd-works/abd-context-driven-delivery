## Story: Activate Sim

### Scenario: Activate Sim

*Given* Mavenir has valid ICCID available in inventory
*When* the Customer activates the SIM with valid ICCID
*Then* My Paradise sends the ICCID inventory request to Mavenir with valid ICCID
*And* My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID
*And* My Paradise sends the pSIM delivered order to Mavenir
*When* Mavenir creates the product order and clears waiting pSIM
*Then* My Paradise stores valid ICCID on the line

### Scenario: waiting pSIM is absent

*Given* Mavenir has valid ICCID available in inventory but the Mavenir customer has no waiting pSIM characteristic
*When* the Customer activates the SIM with valid ICCID
*Then* the pSIM delivered order is rejected

### Scenario: waiting pSIM already completed

*Given* Mavenir has valid ICCID available in inventory and the Mavenir customer has waiting pSIM false
*When* the Customer activates the SIM with valid ICCID
*Then* the pSIM delivered order is rejected
