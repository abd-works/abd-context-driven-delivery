/**
 * Epic: Get Sim
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Choose Esim
 * Actor: Customer
 */

story('Choose Esim', () => {
  background('each', ({ given }) => {
    scenario('Choose eSIM', ({ given, when, then }) => {
      given('no ++SIM type++ is on the line', () => {});
      when('the Customer selects eSIM', () => {});
      then('My Paradise sends the patch cart request to Mavenir with ++SIM type++ eSIM', () => {});
      when('Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ eSIM', () => {});
      then('My Paradise stores eSIM on the line', () => {}).and('the Customer is forwarded to Verify ID', () => {});
    });
    scenario('Choose eSIM — already on the line', ({ given, when, then }) => {
      given('the line already has ++SIM type++ eSIM', () => {});
      when('the Customer selects eSIM', () => {});
      then('My Paradise skips the cart patch', () => {});
    });
    scenario('Choose eSIM — cart patch fails', ({ given, when, then }) => {
      given('Mavenir returns an error on cart patch', () => {});
      when('the Customer selects eSIM', () => {});
      then('the SIM selection fails', () => {}).and('the line has no ++SIM type++', () => {});
    });
  });
});

/**
 * Story: Request a Paradise Sim Card
 * Actor: Customer
 */

story('Request a Paradise Sim Card', () => {
  background('each', ({ given }) => {
    scenario('Request a Paradise SIM card', ({ given, when, then }) => {
      given('no ++SIM type++ is on the line', () => {}).and('no ++ICCID++ is on the line', () => {});
      when('the Customer requests a Paradise SIM card', () => {});
      then('My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM', () => {});
      when('Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM', () => {});
      then('My Paradise stores pSIM on the line', () => {}).but('the line has no ++ICCID++', () => {}).and('the Customer is forwarded to Verify ID', () => {});
    });
    scenario('Request a Paradise SIM card — already on the line', ({ given, when, then }) => {
      given('the line already has ++SIM type++ pSIM', () => {});
      when('the Customer requests a Paradise SIM card', () => {});
      then('My Paradise skips the cart patch', () => {});
    });
    scenario('Request a Paradise SIM card — cart patch fails', ({ given, when, then }) => {
      given('Mavenir returns an error on cart patch', () => {});
      when('the Customer requests a Paradise SIM card', () => {});
      then('the SIM selection fails', () => {}).and('the line has no ++SIM type++', () => {});
    });
  });
});

/**
 * Story: Enter Existing Sim
 * Actor: Customer
 */

story('Enter Existing Sim', () => {
  background('each', ({ given }) => {
    scenario('Enter existing SIM', ({ given, when, then }) => {
      given('Mavenir has ++ICCID++ ++valid ICCID++ available in inventory', () => {});
      when('the Customer attaches ++ICCID++ ++valid ICCID++', () => {});
      then('My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++', () => {}).and('My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++', () => {});
      when('Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++', () => {});
      then('My Paradise stores pSIM and ++ICCID++ ++valid ICCID++ on the line', () => {}).and('the Customer is forwarded to Verify ID', () => {});
    });
    scenario('ICCID contains spaces', ({ given, when, then }) => {
      given('the Customer has ++ICCID++ ++ICCID with spaces++', () => {});
      when('the Customer attaches ++ICCID++ ++ICCID with spaces++', () => {});
      then('the ICCID format is rejected', () => {}).and('My Paradise does not query inventory or patch the cart', () => {});
    });
    scenario('Inventory rejects ICCID', ({ given, when, then }) => {
      given('Mavenir does not have ++ICCID++ ++invalid ICCID++ available in inventory', () => {});
      when('the Customer attaches ++ICCID++ ++invalid ICCID++', () => {});
      then('My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++invalid ICCID++', () => {}).and('My Paradise does not patch the cart', () => {}).and('the ICCID is rejected', () => {});
    });
  });
});

/**
 * Story: Activate Sim
 * Actor: Customer
 */

story('Activate Sim', () => {
  background('each', ({ given }) => {
    scenario('Activate Sim', ({ given, when, then }) => {
      given('Mavenir has ++ICCID++ ++valid ICCID++ available in inventory', () => {});
      when('the Customer activates the SIM with ++ICCID++ ++valid ICCID++', () => {});
      then('My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++', () => {}).and('My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++', () => {}).and('My Paradise sends the pSIM delivered order to Mavenir', () => {});
      when('Mavenir creates the product order and clears ++waiting pSIM++', () => {});
      then('My Paradise stores ++ICCID++ ++valid ICCID++ on the line', () => {});
    });
    scenario('waiting pSIM is absent', ({ given, when, then }) => {
      given('Mavenir has ++ICCID++ ++valid ICCID++ available in inventory', () => {}).but('the ++Mavenir customer++ has no ++waiting pSIM++ characteristic', () => {});
      when('the Customer activates the SIM with ++ICCID++ ++valid ICCID++', () => {});
      then('the pSIM delivered order is rejected', () => {});
    });
    scenario('waiting pSIM already completed', ({ given, when, then }) => {
      given('Mavenir has ++ICCID++ ++valid ICCID++ available in inventory', () => {}).and('the ++Mavenir customer++ has ++waiting pSIM++ Cleared', () => {});
      when('the Customer activates the SIM with ++ICCID++ ++valid ICCID++', () => {});
      then('the pSIM delivered order is rejected', () => {});
    });
  });
});

/**
 * Story: Complete Draft Sim Order
 */

story('Complete Draft Sim Order', () => {
  background('each', ({ given }) => {
    scenario('Complete Draft Sim Order', ({ given, when, then }) => {
      given('Care opens the ++Mavenir customer++ record in Mavenir DEP', () => {}).and('Care sees the draft order in the orders grid (22-dep-orders-grid.png)', () => {});
      when('Care attaches the ++ICCID++ to the draft order and completes it', () => {});
      then('the order status in DEP Order History changes from draft to active (23-dep-order-history.png)', () => {}).and('the ++waiting pSIM++ characteristic on the ++Mavenir customer++ is cleared', () => {});
    });
  });
});
