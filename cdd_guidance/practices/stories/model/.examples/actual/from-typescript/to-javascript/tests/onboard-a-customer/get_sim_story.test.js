/**
 * Epic: Get Sim
 * Orders: 0.0.6
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Choose Esim
 */

story('Choose Esim', () => {
    scenario('Choose eSIM', ({ given, when, then }) => {
      given('no SIM type is on the line', () => {});
      when('the Customer selects eSIM', () => {});
      then('My Paradise sends the patch cart request to Mavenir with SIM type eSIM', () => {});
      when('Mavenir returns the updated Mavenir shopping cart with SIM type eSIM', () => {});
      then('My Paradise stores eSIM on the line', () => {}).but('the line has no ICCID', () => {}).and('the Customer is forwarded to Verify ID', () => {});
    });
    scenario('Choose eSIM — already on the line', ({ given, when, then }) => {
      given('the line already has SIM type eSIM', () => {});
      when('the Customer selects eSIM', () => {});
      then('My Paradise skips the cart patch', () => {});
    });
    scenario('Choose eSIM — cart patch fails', ({ given, when, then }) => {
      given('Mavenir returns an error on cart patch', () => {});
      when('the Customer selects eSIM', () => {});
      then('the SIM selection fails', () => {});
      when('My Paradise reloads the shopping cart', () => {});
      then('the line has no SIM type', () => {}).and('the line has no ICCID', () => {});
    });
});

/**
 * Story: Request a Paradise Sim Card
 */

story('Request a Paradise Sim Card', () => {
    scenario('Request a Paradise SIM card', ({ given, when, then }) => {
      given('no SIM type is on the line and no ICCID is on the line', () => {});
      when('the Customer requests a Paradise SIM card', () => {});
      then('My Paradise sends the patch cart request to Mavenir with SIM type pSIM', () => {});
      when('Mavenir returns the updated Mavenir shopping cart with SIM type pSIM', () => {});
      then('My Paradise stores pSIM on the line', () => {}).but('the line has no ICCID', () => {}).and('the Customer is forwarded to Verify ID', () => {});
    });
    scenario('Request a Paradise SIM card — already on the line', ({ given, when, then }) => {
      given('the line already has SIM type pSIM', () => {});
      when('the Customer requests a Paradise SIM card', () => {});
      then('My Paradise skips the cart patch', () => {});
    });
    scenario('Request a Paradise SIM card — cart patch fails', ({ given, when, then }) => {
      given('Mavenir returns an error on cart patch', () => {});
      when('the Customer requests a Paradise SIM card', () => {});
      then('the SIM selection fails', () => {});
      when('My Paradise reloads the shopping cart', () => {});
      then('the line has no SIM type', () => {}).and('the line has no ICCID', () => {});
    });
});

/**
 * Story: Enter Existing Sim
 */

story('Enter Existing Sim', () => {
    scenario('Enter existing SIM', ({ given, when, then }) => {
      given('Mavenir has valid ICCID available in inventory', () => {});
      when('the Customer attaches valid ICCID', () => {});
      then('My Paradise sends the ICCID inventory request to Mavenir with valid ICCID', () => {}).and('My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID', () => {});
      when('Mavenir returns the updated Mavenir shopping cart with SIM type pSIM and valid ICCID', () => {});
      then('My Paradise stores pSIM and valid ICCID on the line', () => {}).and('the line has valid ICCID', () => {}).and('the Customer is forwarded to Verify ID', () => {});
    });
    scenario('ICCID contains spaces', ({ given, when, then }) => {
      given('the Customer has ICCID with spaces', () => {});
      when('the Customer attaches ICCID with spaces', () => {});
      then('the ICCID format is rejected', () => {}).and('My Paradise does not query inventory or patch the cart', () => {});
    });
    scenario('Inventory rejects ICCID', ({ given, when, then }) => {
      given('Mavenir does not have invalid ICCID available in inventory', () => {});
      when('the Customer attaches invalid ICCID', () => {});
      then('My Paradise sends the ICCID inventory request to Mavenir with invalid ICCID', () => {}).and('My Paradise does not patch the cart', () => {}).and('the ICCID is rejected', () => {});
    });
});

/**
 * Story: Activate Sim
 */

story('Activate Sim', () => {
    scenario('Activate Sim', ({ given, when, then }) => {
      given('Mavenir has valid ICCID available in inventory', () => {});
      when('the Customer activates the SIM with valid ICCID', () => {});
      then('My Paradise sends the ICCID inventory request to Mavenir with valid ICCID', () => {}).and('My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID', () => {}).and('My Paradise sends the pSIM delivered order to Mavenir', () => {});
      when('Mavenir creates the product order and clears waiting pSIM', () => {});
      then('My Paradise stores valid ICCID on the line', () => {});
    });
    scenario('waiting pSIM is absent', ({ given, when, then }) => {
      given('Mavenir has valid ICCID available in inventory but the Mavenir customer has no waiting pSIM characteristic', () => {});
      when('the Customer activates the SIM with valid ICCID', () => {});
      then('the pSIM delivered order is rejected', () => {});
    });
    scenario('waiting pSIM already completed', ({ given, when, then }) => {
      given('Mavenir has valid ICCID available in inventory and the Mavenir customer has waiting pSIM false', () => {});
      when('the Customer activates the SIM with valid ICCID', () => {});
      then('the pSIM delivered order is rejected', () => {});
    });
});
