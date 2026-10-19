/**
 * Epic: Get Sim
 * Orders: 0.0.6
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Choose Esim
 */

story('Choose Esim', () => {
  scenario('Choose eSIM', ({ given, when, then }) => {
    given('no SIM type is on the line', () => {
      // TODO: implement step
    });
    when('the Customer selects eSIM', () => {
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with SIM type eSIM', () => {
      // TODO: implement step
    });
    when('Mavenir returns the updated Mavenir shopping cart with SIM type eSIM', () => {
      // TODO: implement step
    });
    then('My Paradise stores eSIM on the line', () => {
      // TODO: implement step
    })
      .but('the line has no ICCID', () => {
        // TODO: implement step
      })
      .and('the Customer is forwarded to Verify ID', () => {
        // TODO: implement step
      });
  });

  scenario('Choose eSIM — already on the line', ({ given, when, then }) => {
    given('the line already has SIM type eSIM', () => {
      // TODO: implement step
    });
    when('the Customer selects eSIM', () => {
      // TODO: implement step
    });
    then('My Paradise skips the cart patch', () => {
      // TODO: implement step
    });
  });

  scenario('Choose eSIM — cart patch fails', ({ given, when, then }) => {
    given('Mavenir returns an error on cart patch', () => {
      // TODO: implement step
    });
    when('the Customer selects eSIM', () => {
      // TODO: implement step
    });
    then('the SIM selection fails', () => {
      // TODO: implement step
    });
    when('My Paradise reloads the shopping cart', () => {
      // TODO: implement step
    });
    then('the line has no SIM type', () => {
      // TODO: implement step
    })
      .and('the line has no ICCID', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Request a Paradise Sim Card
 */

story('Request a Paradise Sim Card', () => {
  scenario('Request a Paradise SIM card', ({ given, when, then }) => {
    given('no SIM type is on the line and no ICCID is on the line', () => {
      // TODO: implement step
    });
    when('the Customer requests a Paradise SIM card', () => {
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with SIM type pSIM', () => {
      // TODO: implement step
    });
    when('Mavenir returns the updated Mavenir shopping cart with SIM type pSIM', () => {
      // TODO: implement step
    });
    then('My Paradise stores pSIM on the line', () => {
      // TODO: implement step
    })
      .but('the line has no ICCID', () => {
        // TODO: implement step
      })
      .and('the Customer is forwarded to Verify ID', () => {
        // TODO: implement step
      });
  });

  scenario('Request a Paradise SIM card — already on the line', ({ given, when, then }) => {
    given('the line already has SIM type pSIM', () => {
      // TODO: implement step
    });
    when('the Customer requests a Paradise SIM card', () => {
      // TODO: implement step
    });
    then('My Paradise skips the cart patch', () => {
      // TODO: implement step
    });
  });

  scenario('Request a Paradise SIM card — cart patch fails', ({ given, when, then }) => {
    given('Mavenir returns an error on cart patch', () => {
      // TODO: implement step
    });
    when('the Customer requests a Paradise SIM card', () => {
      // TODO: implement step
    });
    then('the SIM selection fails', () => {
      // TODO: implement step
    });
    when('My Paradise reloads the shopping cart', () => {
      // TODO: implement step
    });
    then('the line has no SIM type', () => {
      // TODO: implement step
    })
      .and('the line has no ICCID', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Enter Existing Sim
 */

story('Enter Existing Sim', () => {
  scenario('Enter existing SIM', ({ given, when, then }) => {
    given('Mavenir has valid ICCID available in inventory', () => {
      // TODO: implement step
    });
    when('the Customer attaches valid ICCID', () => {
      // TODO: implement step
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with valid ICCID', () => {
      // TODO: implement step
    })
      .and('My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID', () => {
        // TODO: implement step
      });
    when('Mavenir returns the updated Mavenir shopping cart with SIM type pSIM and valid ICCID', () => {
      // TODO: implement step
    });
    then('My Paradise stores pSIM and valid ICCID on the line', () => {
      // TODO: implement step
    })
      .and('the line has valid ICCID', () => {
        // TODO: implement step
      })
      .and('the Customer is forwarded to Verify ID', () => {
        // TODO: implement step
      });
  });

  scenario('ICCID contains spaces', ({ given, when, then }) => {
    given('the Customer has ICCID with spaces', () => {
      // TODO: implement step
    });
    when('the Customer attaches ICCID with spaces', () => {
      // TODO: implement step
    });
    then('the ICCID format is rejected', () => {
      // TODO: implement step
    })
      .and('My Paradise does not query inventory or patch the cart', () => {
        // TODO: implement step
      });
  });

  scenario('Inventory rejects ICCID', ({ given, when, then }) => {
    given('Mavenir does not have invalid ICCID available in inventory', () => {
      // TODO: implement step
    });
    when('the Customer attaches invalid ICCID', () => {
      // TODO: implement step
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with invalid ICCID', () => {
      // TODO: implement step
    })
      .and('My Paradise does not patch the cart', () => {
        // TODO: implement step
      })
      .and('the ICCID is rejected', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Activate Sim
 */

story('Activate Sim', () => {
  scenario('Activate Sim', ({ given, when, then }) => {
    given('Mavenir has valid ICCID available in inventory', () => {
      // TODO: implement step
    });
    when('the Customer activates the SIM with valid ICCID', () => {
      // TODO: implement step
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with valid ICCID', () => {
      // TODO: implement step
    })
      .and('My Paradise sends the patch cart request to Mavenir with SIM type pSIM and valid ICCID', () => {
        // TODO: implement step
      })
      .and('My Paradise sends the pSIM delivered order to Mavenir', () => {
        // TODO: implement step
      });
    when('Mavenir creates the product order and clears waiting pSIM', () => {
      // TODO: implement step
    });
    then('My Paradise stores valid ICCID on the line', () => {
      // TODO: implement step
    });
  });

  scenario('waiting pSIM is absent', ({ given, when, then }) => {
    given('Mavenir has valid ICCID available in inventory but the Mavenir customer has no waiting pSIM characteristic', () => {
      // TODO: implement step
    });
    when('the Customer activates the SIM with valid ICCID', () => {
      // TODO: implement step
    });
    then('the pSIM delivered order is rejected', () => {
      // TODO: implement step
    });
  });

  scenario('waiting pSIM already completed', ({ given, when, then }) => {
    given('Mavenir has valid ICCID available in inventory and the Mavenir customer has waiting pSIM false', () => {
      // TODO: implement step
    });
    when('the Customer activates the SIM with valid ICCID', () => {
      // TODO: implement step
    });
    then('the pSIM delivered order is rejected', () => {
      // TODO: implement step
    });
  });

});
