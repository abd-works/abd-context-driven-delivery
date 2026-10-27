// Epic: Get Sim
// Orders: 0.0.6

/** Story: Choose Esim
 * SCENARIO: Choose eSIM
 * GIVEN: no SIM type is on the line
 * WHEN: the Customer selects eSIM
 * THEN: My Paradise sends the patch cart request to Mavenir with SIM type eSIM
 * WHEN: Mavenir returns the updated Mavenir shopping cart with SIM type eSIM
 * THEN: My Paradise stores eSIM on the line
 * BUT: the line has no ICCID
 * AND: the Customer is forwarded to Verify ID
 * SCENARIO: Choose eSIM — already on the line
 * GIVEN: the line already has SIM type eSIM
 * WHEN: the Customer selects eSIM
 * THEN: My Paradise skips the cart patch
 * SCENARIO: Choose eSIM — cart patch fails
 * GIVEN: Mavenir returns an error on cart patch
 * WHEN: the Customer selects eSIM
 * THEN: the SIM selection fails
 * WHEN: My Paradise reloads the shopping cart
 * THEN: the line has no SIM type
 * AND: the line has no ICCID
 */

/** Story: Request a Paradise Sim Card
 * SCENARIO: Request a Paradise SIM card
 * GIVEN: no SIM type is on the line and no ICCID is on the line
 * WHEN: the Customer requests a Paradise SIM card
 * THEN: My Paradise sends the patch cart request to Mavenir with SIM type pSIM
 * WHEN: Mavenir returns the updated Mavenir shopping cart with SIM type pSIM
 * THEN: My Paradise stores pSIM on the line
 * BUT: the line has no ICCID
 * AND: the Customer is forwarded to Verify ID
 * SCENARIO: Request a Paradise SIM card — already on the line
 * GIVEN: the line already has SIM type pSIM
 * WHEN: the Customer requests a Paradise SIM card
 * THEN: My Paradise skips the cart patch
 * SCENARIO: Request a Paradise SIM card — cart patch fails
 * GIVEN: Mavenir returns an error on cart patch
 * WHEN: the Customer requests a Paradise SIM card
 * THEN: the SIM selection fails
 * WHEN: My Paradise reloads the shopping cart
 * THEN: the line has no SIM type
 * AND: the line has no ICCID
 */

/** Story: Enter Existing Sim
 * SCENARIO: Enter existing SIM
 * GIVEN: Mavenir has valid ICCID available in inventory
 * WHEN: the Customer attaches valid ICCID
 * THEN: My Paradise sends the ICCID inventory request to Mavenir with valid ICCID
 * AND: My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID
 * WHEN: Mavenir returns the updated Mavenir shopping cart with SIM type pSIM and valid ICCID
 * THEN: My Paradise stores pSIM and valid ICCID on the line
 * AND: the line has valid ICCID
 * AND: the Customer is forwarded to Verify ID
 * SCENARIO: ICCID contains spaces
 * GIVEN: the Customer has ICCID with spaces
 * WHEN: the Customer attaches ICCID with spaces
 * THEN: the ICCID format is rejected
 * AND: My Paradise does not query inventory or patch the cart
 * SCENARIO: Inventory rejects ICCID
 * GIVEN: Mavenir does not have invalid ICCID available in inventory
 * WHEN: the Customer attaches invalid ICCID
 * THEN: My Paradise sends the ICCID inventory request to Mavenir with invalid ICCID
 * AND: My Paradise does not patch the cart
 * AND: the ICCID is rejected
 */

/** Story: Activate Sim
 * SCENARIO: Activate Sim
 * GIVEN: Mavenir has valid ICCID available in inventory
 * WHEN: the Customer activates the SIM with valid ICCID
 * THEN: My Paradise sends the ICCID inventory request to Mavenir with valid ICCID
 * AND: My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID
 * AND: My Paradise sends the pSIM delivered order to Mavenir
 * WHEN: Mavenir creates the product order and clears waiting pSIM
 * THEN: My Paradise stores valid ICCID on the line
 * SCENARIO: waiting pSIM is absent
 * GIVEN: Mavenir has valid ICCID available in inventory but the Mavenir customer has no waiting pSIM characteristic
 * WHEN: the Customer activates the SIM with valid ICCID
 * THEN: the pSIM delivered order is rejected
 * SCENARIO: waiting pSIM already completed
 * GIVEN: Mavenir has valid ICCID available in inventory and the Mavenir customer has waiting pSIM false
 * WHEN: the Customer activates the SIM with valid ICCID
 * THEN: the pSIM delivered order is rejected
 */
