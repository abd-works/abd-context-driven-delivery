/**
 * Epic: Get Sim
 * Orders: 0.0.4
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Choose Esim
 * Actor: Customer
 */

story('Choose Esim', () => {
  scenario('Choose eSIM', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('eSIM is available', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('the phone supports eSIM', () => {
          // TODO: implement step
        });
    });
    given('no ++SIM type++ is on the line', () => {
      // TODO: implement step
    });
    when('the Customer selects eSIM', () => {
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with ++SIM type++ eSIM', () => {
      // TODO: implement step
    });
    when('Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ eSIM', () => {
      // TODO: implement step
    });
    then('My Paradise stores eSIM on the line', () => {
      // TODO: implement step
    })
      .and('the Customer is forwarded to Verify ID', () => {
        // TODO: implement step
      });
  });

  scenario('Choose eSIM — already on the line', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('eSIM is available', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('the phone supports eSIM', () => {
          // TODO: implement step
        });
    });
    given('the line already has ++SIM type++ eSIM', () => {
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
    background('background', ({ given }) => {
      given('eSIM is available', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .and('the phone supports eSIM', () => {
          // TODO: implement step
        });
    });
    given('Mavenir returns an error on cart patch', () => {
      // TODO: implement step
    });
    when('the Customer selects eSIM', () => {
      // TODO: implement step
    });
    then('the SIM selection fails', () => {
      // TODO: implement step
    })
      .and('the line has no ++SIM type++', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Request a Paradise Sim Card
 * Actor: Customer
 */

story('Request a Paradise Sim Card', () => {
  scenario('Request a Paradise SIM card', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer is choosing a physical SIM', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('no ++SIM type++ is on the line', () => {
      // TODO: implement step
    })
      .and('no ++ICCID++ is on the line', () => {
        // TODO: implement step
      });
    when('the Customer requests a Paradise SIM card', () => {
      // TODO: implement step
    });
    then('My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM', () => {
      // TODO: implement step
    });
    when('Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM', () => {
      // TODO: implement step
    });
    then('My Paradise stores pSIM on the line', () => {
      // TODO: implement step
    })
      .but('the line has no ++ICCID++', () => {
        // TODO: implement step
      })
      .and('the Customer is forwarded to Verify ID', () => {
        // TODO: implement step
      });
  });

  scenario('Request a Paradise SIM card — already on the line', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer is choosing a physical SIM', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('the line already has ++SIM type++ pSIM', () => {
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
    background('background', ({ given }) => {
      given('the Customer is choosing a physical SIM', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('Mavenir returns an error on cart patch', () => {
      // TODO: implement step
    });
    when('the Customer requests a Paradise SIM card', () => {
      // TODO: implement step
    });
    then('the SIM selection fails', () => {
      // TODO: implement step
    })
      .and('the line has no ++SIM type++', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Enter Existing Sim
 * Actor: Customer
 */

story('Enter Existing Sim', () => {
  scenario('Enter existing SIM', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer is choosing a physical SIM', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('Mavenir has ++ICCID++ ++valid ICCID++ available in inventory', () => {
      // TODO: implement step
    });
    when('the Customer attaches ++ICCID++ ++valid ICCID++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++', () => {
      // TODO: implement step
    })
      .and('My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++', () => {
        // TODO: implement step
      });
    when('Mavenir returns the updated ++Mavenir shopping cart++ with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++', () => {
      // TODO: implement step
    });
    then('My Paradise stores pSIM and ++ICCID++ ++valid ICCID++ on the line', () => {
      // TODO: implement step
    })
      .and('the Customer is forwarded to Verify ID', () => {
        // TODO: implement step
      });
  });

  scenario('ICCID contains spaces', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer is choosing a physical SIM', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('the Customer has ++ICCID++ ++ICCID with spaces++', () => {
      // TODO: implement step
    });
    when('the Customer attaches ++ICCID++ ++ICCID with spaces++', () => {
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
    background('background', ({ given }) => {
      given('the Customer is choosing a physical SIM', () => {
        // TODO: implement step
      })
        .and('the Customer has a ++My Paradise customer++ with ++available number++ ++chosen available number++ in the ++Mavenir shopping cart++', () => {
          // TODO: implement step
        });
    });
    given('Mavenir does not have ++ICCID++ ++invalid ICCID++ available in inventory', () => {
      // TODO: implement step
    });
    when('the Customer attaches ++ICCID++ ++invalid ICCID++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++invalid ICCID++', () => {
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
 * Actor: Customer
 */

story('Activate Sim', () => {
  scenario('Activate Sim', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer is waiting for a Paradise SIM', () => {
        // TODO: implement step
      })
        .and('the Customer is verified', () => {
          // TODO: implement step
        })
        .and('the line has ++SIM type++ pSIM', () => {
          // TODO: implement step
        })
        .but('no ++ICCID++ is on the line', () => {
          // TODO: implement step
        })
        .and('the ++Mavenir customer++ has ++waiting pSIM++ Active', () => {
          // TODO: implement step
        });
    });
    given('Mavenir has ++ICCID++ ++valid ICCID++ available in inventory', () => {
      // TODO: implement step
    });
    when('the Customer activates the SIM with ++ICCID++ ++valid ICCID++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the ICCID inventory request to Mavenir with ++ICCID++ ++valid ICCID++', () => {
      // TODO: implement step
    })
      .and('My Paradise sends the patch cart request to Mavenir with ++SIM type++ pSIM and ++ICCID++ ++valid ICCID++', () => {
        // TODO: implement step
      })
      .and('My Paradise sends the pSIM delivered order to Mavenir', () => {
        // TODO: implement step
      });
    when('Mavenir creates the product order and clears ++waiting pSIM++', () => {
      // TODO: implement step
    });
    then('My Paradise stores ++ICCID++ ++valid ICCID++ on the line', () => {
      // TODO: implement step
    });
  });

  scenario('waiting pSIM is absent', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer is waiting for a Paradise SIM', () => {
        // TODO: implement step
      })
        .and('the Customer is verified', () => {
          // TODO: implement step
        })
        .and('the line has ++SIM type++ pSIM', () => {
          // TODO: implement step
        })
        .but('no ++ICCID++ is on the line', () => {
          // TODO: implement step
        })
        .and('the ++Mavenir customer++ has ++waiting pSIM++ Active', () => {
          // TODO: implement step
        });
    });
    given('Mavenir has ++ICCID++ ++valid ICCID++ available in inventory', () => {
      // TODO: implement step
    })
      .but('the ++Mavenir customer++ has no ++waiting pSIM++ characteristic', () => {
        // TODO: implement step
      });
    when('the Customer activates the SIM with ++ICCID++ ++valid ICCID++', () => {
      // TODO: implement step
    });
    then('the pSIM delivered order is rejected', () => {
      // TODO: implement step
    });
  });

  scenario('waiting pSIM already completed', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the Customer is waiting for a Paradise SIM', () => {
        // TODO: implement step
      })
        .and('the Customer is verified', () => {
          // TODO: implement step
        })
        .and('the line has ++SIM type++ pSIM', () => {
          // TODO: implement step
        })
        .but('no ++ICCID++ is on the line', () => {
          // TODO: implement step
        })
        .and('the ++Mavenir customer++ has ++waiting pSIM++ Active', () => {
          // TODO: implement step
        });
    });
    given('Mavenir has ++ICCID++ ++valid ICCID++ available in inventory', () => {
      // TODO: implement step
    })
      .and('the ++Mavenir customer++ has ++waiting pSIM++ Cleared', () => {
        // TODO: implement step
      });
    when('the Customer activates the SIM with ++ICCID++ ++valid ICCID++', () => {
      // TODO: implement step
    });
    then('the pSIM delivered order is rejected', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Complete Draft Sim Order
 */

story('Complete Draft Sim Order', () => {
  scenario('Complete Draft Sim Order', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('a Customer completed the My Paradise onboarding flow', () => {
        // TODO: implement step
      })
        .and('the Customer\'s line has ++SIM type++ pSIM', () => {
          // TODO: implement step
        })
        .but('the Customer never entered an ++ICCID++', () => {
          // TODO: implement step
        })
        .and('the ++Mavenir customer++ has ++waiting pSIM++ Active', () => {
          // TODO: implement step
        });
    });
    given('Care opens the ++Mavenir customer++ record in Mavenir DEP', () => {
      // TODO: implement step
    })
      .and('Care sees the draft order in the orders grid (`22-dep-orders-grid.png`)', () => {
        // TODO: implement step
      });
    when('Care attaches the ++ICCID++ to the draft order and completes it', () => {
      // TODO: implement step
    });
    then('the order status in DEP Order History changes from draft to active (`23-dep-order-history.png`)', () => {
      // TODO: implement step
    })
      .and('the ++waiting pSIM++ characteristic on the ++Mavenir customer++ is cleared', () => {
        // TODO: implement step
      });
  });

});
