/**
 * Epic: Create Customer
 * Orders: 0.0.1
 */

import { scenario, story } from "tests/story-test";

/**
 * Story: Enter Account Credentials
 */

// background-examples: {"email required": {"account credential requirements": "account credential requirements", "example": "email required", "field": "email", "requirement": "Email is required", "group": "Account credential requirements"}, "email format": {"account credential requirements": "account credential requirements", "example": "email format", "field": "email", "requirement": "Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com)", "group": "Account credential requirements"}, "password letters": {"account credential requirements": "account credential requirements", "example": "password letters", "field": "password", "requirement": "Password must contain uppercase and lowercase letters", "group": "Account credential requirements"}, "password number": {"account credential requirements": "account credential requirements", "example": "password number", "field": "password", "requirement": "Password must have at least one number", "group": "Account credential requirements"}, "password symbol": {"account credential requirements": "account credential requirements", "example": "password symbol", "field": "password", "requirement": "Password must have at least one symbol", "group": "Account credential requirements"}, "password length": {"account credential requirements": "account credential requirements", "example": "password length", "field": "password", "requirement": "Length must be greater than 8 characters", "group": "Account credential requirements"}, "confirm required": {"account credential requirements": "account credential requirements", "example": "confirm required", "field": "confirmPassword", "requirement": "Confirm Password is required", "group": "Account credential requirements"}, "confirm mismatch": {"account credential requirements": "account credential requirements", "example": "confirm mismatch", "field": "confirmPassword", "requirement": "Passwords don't match", "group": "Account credential requirements"}, "example": {"account credential requirements": "account credentials", "example": "example", "field": "unmet", "requirement": "Create account", "group": "Account credential requirements"}, "valid account credentials": {"account credential requirements": "account credentials", "example": "valid account credentials", "field": "", "requirement": "enabled", "group": "Account credential requirements"}, "Paradise Mobile account credentials": {"account credential requirements": "account credentials", "example": "Paradise Mobile account credentials", "field": "", "requirement": "enabled", "group": "Account credential requirements"}, "invalid password letters": {"account credential requirements": "account credentials", "example": "invalid password letters", "field": "Password must contain uppercase and lowercase letters", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password number": {"account credential requirements": "account credentials", "example": "invalid password number", "field": "Password must have at least one number", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password symbol": {"account credential requirements": "account credentials", "example": "invalid password symbol", "field": "Password must have at least one symbol", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password length": {"account credential requirements": "account credentials", "example": "invalid password length", "field": "Length must be greater than 8 characters", "requirement": "disabled", "group": "Account credential requirements"}, "invalid confirm required": {"account credential requirements": "account credentials", "example": "invalid confirm required", "field": "Confirm Password is required", "requirement": "disabled", "group": "Account credential requirements"}, "invalid confirm mismatch": {"account credential requirements": "account credentials", "example": "invalid confirm mismatch", "field": "Passwords don't match", "requirement": "disabled", "group": "Account credential requirements"}, "invalid email required": {"account credential requirements": "account credentials", "example": "invalid email required", "field": "Email is required", "requirement": "disabled", "group": "Account credential requirements"}, "invalid email format": {"account credential requirements": "account credentials", "example": "invalid email format", "field": "Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com)", "requirement": "disabled", "group": "Account credential requirements"}}
story('Enter Account Credentials', () => {
  background('background', ({ given }) => {
  });

  scenario('Enter new account credentials', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      })
        .and('the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site', () => {
          // TODO: implement step
        });
    });
    when('the User proceeds to create an account from the Paradise Mobile website', () => {
      // TODO: implement step
    });
    then('the User can enter ++account credentials++', () => {
      // TODO: implement step
    })
      .and('++account credential requirements++ are shown in black (Email is required, password rules)', () => {
        // TODO: implement step
      })
      .and('the Create account operation is disabled', () => {
        // TODO: implement step
      })
      .and('the User can Sign in', () => {
        // TODO: implement step
      })
      .and('the User can go Back', () => {
        // TODO: implement step
      })
      .and('the User can open Service Agreement, Terms and Conditions, and Privacy Policy', () => {
        // TODO: implement step
      });
    when('the User validates ++account credentials++ {example}', () => {
      // TODO: implement step
    });
    then('++account credentials++ are validated continuously as the User types', () => {
      // TODO: implement step
    })
      .and('unmet ++account credential requirements++ {unmet} are red with ✖', () => {
        // TODO: implement step
      })
      .and('the Create account button is {Create account}', () => {
        // TODO: implement step
      });
    when('the User clicks on Create account', () => {
      // TODO: implement step
    });
    then('the system creates an unconfirmed Cognito user routing through Amplify to Cognito', () => {
      // TODO: implement step
    })
      .and('the User is forwarded to check their email', () => {
        // TODO: implement step
      });
  });

  scenario('Paradise Mobile email', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      })
        .and('the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site', () => {
          // TODO: implement step
        });
    });
    when('the User enters ++account credentials++ ++Paradise Mobile account credentials++', () => {
      // TODO: implement step
    });
    then('the Create Account title is blue', () => {
      // TODO: implement step
    });
  });

  scenario('Email already registered', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the plan catalog contains purchasable plans', () => {
        // TODO: implement step
      })
        .and('the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site', () => {
          // TODO: implement step
        });
    });
    given('++account credentials++ ++already-registered account credentials++ are already registered', () => {
      // TODO: implement step
    });
    when('the User registers ++account credentials++ ++already-registered account credentials++', () => {
      // TODO: implement step
    });
    then('Email shows the already-registered error', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Create Unconfirmed Cognito User
 */

story('Create Unconfirmed Cognito User', () => {
  scenario('Create Unconfirmed Cognito User', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++', () => {
        // TODO: implement step
      });
    });
    when('Cognito is asked to register ++account credentials++ ++valid account credentials++', () => {
      // TODO: implement step
    });
    then('Cognito creates ++Cognito user++ ++unconfirmed Cognito user++', () => {
      // TODO: implement step
    })
      .and('Cognito emails a ++validation code++ for those ++account credentials++', () => {
        // TODO: implement step
      })
      .but('no ++account token++ is issued', () => {
        // TODO: implement step
      })
      .but('no ++Mavenir customer++ exists for those ++account credentials++', () => {
        // TODO: implement step
      });
  });

  scenario('Email already registered in Cognito', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++', () => {
        // TODO: implement step
      });
    });
    given('++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++', () => {
      // TODO: implement step
    });
    when('Cognito is asked to register ++account credentials++ ++already-registered account credentials++', () => {
      // TODO: implement step
    });
    then('Cognito returns ++UsernameExistsException++', () => {
      // TODO: implement step
    })
      .and('Cognito does not create another ++Cognito user++ for those ++account credentials++', () => {
        // TODO: implement step
      });
  });

  scenario('Cognito register fails with another error', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++', () => {
        // TODO: implement step
      });
    });
  });

});

/**
 * Story: Enter Validation Code
 * Actor: My Paradise
 */

// background-examples: {"valid validation code": {"validation code": "validation code", "example": "valid validation code", "code": "123456", "group": "validation code"}, "mismatch validation code": {"validation code": "validation code", "example": "mismatch validation code", "code": "Hmm. That code didn't work.", "group": "validation code"}, "expired validation code": {"validation code": "validation code", "example": "expired validation code", "code": "Hmm. That code didn't work.", "group": "validation code"}, "attempts exceeded validation code": {"validation code": "validation code", "example": "attempts exceeded validation code", "code": "Attempts limit exceeded. Please try again later.", "group": "validation code"}, "example": {"validation code": "validation code", "example": "example", "code": "helper", "group": "validation code"}}
story('Enter Validation Code', () => {
  background('background', ({ given }) => {
  });

  scenario('Enter validation code', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the User has submitted ++account credentials++ ++valid account credentials++', () => {
        // TODO: implement step
      })
        .and('Cognito has an ++Cognito user++ ++unconfirmed Cognito user++', () => {
          // TODO: implement step
        });
    });
    when('the User proceeds to check their email', () => {
      // TODO: implement step
    });
    then('the User sees the code was sent to *[Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com)*', () => {
      // TODO: implement step
    })
      .and('the User can enter a ++validation code++ in Enter Validation Code', () => {
        // TODO: implement step
      })
      .and('the User can Resend', () => {
        // TODO: implement step
      })
      .and('the User can Close', () => {
        // TODO: implement step
      })
      .and('the Activate account operation is disabled', () => {
        // TODO: implement step
      });
    when('the User enters a ++validation code++ ++valid validation code++', () => {
      // TODO: implement step
    });
    then('the Activate account operation is enabled', () => {
      // TODO: implement step
    });
    when('the User clicks Activate account', () => {
      // TODO: implement step
    });
    then('the system confirms the ++Cognito user++ routing through Amplify to Cognito', () => {
      // TODO: implement step
    })
      .and('the User is forwarded to onboarding', () => {
        // TODO: implement step
      });
  });

  scenario('Activate with unusable validation code', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the User has submitted ++account credentials++ ++valid account credentials++', () => {
        // TODO: implement step
      })
        .and('Cognito has an ++Cognito user++ ++unconfirmed Cognito user++', () => {
          // TODO: implement step
        });
    });
    when('the User clicks Activate account with ++validation code++ {scenario}', () => {
      // TODO: implement step
    });
    then('Enter Validation Code shows helper text {helper}', () => {
      // TODO: implement step
    });
  });

  scenario('Resend validation code', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the User has submitted ++account credentials++ ++valid account credentials++', () => {
        // TODO: implement step
      })
        .and('Cognito has an ++Cognito user++ ++unconfirmed Cognito user++', () => {
          // TODO: implement step
        });
    });
    when('the User clicks Resend', () => {
      // TODO: implement step
    });
    then('the system emails a new ++validation code++ routing through Amplify to Cognito', () => {
      // TODO: implement step
    })
      .and('the User sees *We sent you a new code. Please check your email.*', () => {
        // TODO: implement step
      })
      .and('Resend waits 60 seconds before it can be used again', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Confirm Cognito User
 */

// background-examples: {"mismatch validation code": {"validation code": "validation code", "example": "mismatch validation code", "error": "CodeMismatchException"}, "expired validation code": {"validation code": "validation code", "example": "expired validation code", "error": "ExpiredCodeException"}, "attempts exceeded validation code": {"validation code": "validation code", "example": "attempts exceeded validation code", "error": "LimitExceededException"}}
story('Confirm Cognito User', () => {
  background('background', ({ given }) => {
  });

  scenario('Confirm Cognito User', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('Cognito has an ++Cognito user++ ++unconfirmed Cognito user++', () => {
        // TODO: implement step
      });
    });
    when('Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++', () => {
      // TODO: implement step
    });
    then('Cognito confirms the ++Cognito user++', () => {
      // TODO: implement step
    })
      .but('no ++account token++ is issued', () => {
        // TODO: implement step
      })
      .but('no ++Mavenir customer++ exists for those ++account credentials++', () => {
        // TODO: implement step
      });
  });

  scenario('Confirm with unusable validation code', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('Cognito has an ++Cognito user++ ++unconfirmed Cognito user++', () => {
        // TODO: implement step
      });
    });
    when('Cognito is asked to confirm the user with ++validation code++ {scenario}', () => {
      // TODO: implement step
    });
    then('Cognito returns {error}', () => {
      // TODO: implement step
    })
      .and('Cognito does not confirm the ++Cognito user++', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Issue Account Token To Browser Session
 */

story('Issue Account Token To Browser Session', () => {
  scenario('Issue Account Token To Browser Session', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('Cognito has a ++Cognito user++ ++confirmed Cognito user++', () => {
        // TODO: implement step
      });
    });
    when('Cognito is asked to authenticate ++account credentials++ ++valid account credentials++', () => {
      // TODO: implement step
    });
    then('Cognito issues an ++account token++ for the ++Cognito user++', () => {
      // TODO: implement step
    })
      .but('no ++Mavenir customer++ exists for those ++account credentials++', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Validate Mavenir Customer in Cognito User Attributes
 */

story('Validate Mavenir Customer in Cognito User Attributes', () => {
  scenario('Cognito User already has a Mavenir Customer id', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the User is in Account Setup', () => {
        // TODO: implement step
      })
        .and('Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++', () => {
          // TODO: implement step
        });
    });
    given('the ++Cognito user++ has a ++Mavenir customer++ id', () => {
      // TODO: implement step
    });
    when('the User proceeds to Account Setup', () => {
      // TODO: implement step
    });
    then('My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito', () => {
      // TODO: implement step
    })
      .and('My Paradise finds the ++Mavenir customer++ id on the ++Cognito user++', () => {
        // TODO: implement step
      })
      .and('My Paradise proceeds to load the ++My Paradise customer++ from Midtier', () => {
        // TODO: implement step
      });
  });

  scenario('Cognito User has no Mavenir Customer id', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the User is in Account Setup', () => {
        // TODO: implement step
      })
        .and('Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++', () => {
          // TODO: implement step
        });
    });
    but('no ++Mavenir customer++ exists for those ++account credentials++', () => {
      // TODO: implement step
    });
    when('the User proceeds to Account Setup', () => {
      // TODO: implement step
    });
    then('My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito', () => {
      // TODO: implement step
    })
      .and('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Submit Create Customer Request to Mid-Tier
 */

story('Submit Create Customer Request to Mid-Tier', () => {
  scenario('Submit Create Customer Request to Mid-Tier', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the ++Cognito user++ has no ++Mavenir customer++ id', () => {
        // TODO: implement step
      })
        .and('the browser session has an ++account token++', () => {
          // TODO: implement step
        });
    });
    when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {
      // TODO: implement step
    });
    then('My Paradise adds a ++Mavenir customer++ through the Midtier', () => {
      // TODO: implement step
    });
  });

  scenario('Email already has a Mavenir Customer', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the ++Cognito user++ has no ++Mavenir customer++ id', () => {
        // TODO: implement step
      })
        .and('the browser session has an ++account token++', () => {
          // TODO: implement step
        });
    });
    given('a ++Mavenir customer++ already exists for that email', () => {
      // TODO: implement step
    });
    when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {
      // TODO: implement step
    });
    then('My Paradise shows *Could not create customer.*', () => {
      // TODO: implement step
    });
  });

  scenario('Invalid Account Token', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the ++Cognito user++ has no ++Mavenir customer++ id', () => {
        // TODO: implement step
      })
        .and('the browser session has an ++account token++', () => {
          // TODO: implement step
        });
    });
    given('the ++account token++ is invalid', () => {
      // TODO: implement step
    });
    when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {
      // TODO: implement step
    });
    then('My Paradise shows *Could not create customer.*', () => {
      // TODO: implement step
    });
  });

  scenario('Mavenir is unreachable', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the ++Cognito user++ has no ++Mavenir customer++ id', () => {
        // TODO: implement step
      })
        .and('the browser session has an ++account token++', () => {
          // TODO: implement step
        });
    });
    given('Mavenir has no HTTP response', () => {
      // TODO: implement step
    });
    when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {
      // TODO: implement step
    });
    then('My Paradise shows *Could not create customer.*', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Validate Cognito User
 */

story('Validate Cognito User', () => {
  scenario('Validate Cognito User', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the User has an ++account token++', () => {
        // TODO: implement step
      });
    });
    when('Midtier is asked to validate the ++account token++', () => {
      // TODO: implement step
    });
    then('Midtier verifies the ++account token++', () => {
      // TODO: implement step
    })
      .and('Midtier reads the email from the ++account token++', () => {
        // TODO: implement step
      });
    when('the ++account token++ is invalid', () => {
      // TODO: implement step
    });
    then('Midtier returns "Invalid token"', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Submit Create Mavenir Customer
 */

story('Submit Create Mavenir Customer', () => {
  scenario('Submit Create Mavenir Customer', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('Midtier has verified the ++account token++', () => {
        // TODO: implement step
      })
        .and('the ++account token++ has an email', () => {
          // TODO: implement step
        });
    });
    when('Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++', () => {
      // TODO: implement step
    });
    then('Midtier maps that request to a Mavenir createaccounts for a ++Mavenir customer++ (email and ++contact medium++ from that email)', () => {
      // TODO: implement step
    })
      .and('Midtier submits createaccounts to Mavenir', () => {
        // TODO: implement step
      })
      .and('Midtier receives a Mavenir createaccounts response with the ++Mavenir customer++ id', () => {
        // TODO: implement step
      })
      .and('Midtier maps that ++Mavenir customer++ id to a ++PML customer++ id', () => {
        // TODO: implement step
      })
      .and('Midtier returns the ++PML customer++ id', () => {
        // TODO: implement step
      });
  });

  scenario('Mavenir customer already exists', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('Midtier has verified the ++account token++', () => {
        // TODO: implement step
      })
        .and('the ++account token++ has an email', () => {
          // TODO: implement step
        });
    });
    given('a ++Mavenir customer++ already exists for that email', () => {
      // TODO: implement step
    });
    when('Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++', () => {
      // TODO: implement step
    });
    then('Midtier receives a Mavenir createaccounts conflict', () => {
      // TODO: implement step
    })
      .and('Midtier maps that conflict to Paradise 409', () => {
        // TODO: implement step
      })
      .and('Midtier returns 409', () => {
        // TODO: implement step
      });
  });

  scenario('Mavenir is unreachable', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('Midtier has verified the ++account token++', () => {
        // TODO: implement step
      })
        .and('the ++account token++ has an email', () => {
          // TODO: implement step
        });
    });
    given('Mavenir has no HTTP response', () => {
      // TODO: implement step
    });
    when('Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++', () => {
      // TODO: implement step
    });
    then('Midtier maps that missing response to Paradise 504', () => {
      // TODO: implement step
    })
      .and('Midtier returns 504', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Create Customer
 * Actor: My Paradise
 */

story('Create Customer', () => {
  scenario('Create Customer', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('no ++Mavenir customer++ for that email', () => {
        // TODO: implement step
      })
        .and('Mavenir has that ++account token++ on the create request', () => {
          // TODO: implement step
        });
    });
    when('Mavenir is asked to create a ++Mavenir customer++ for that email', () => {
      // TODO: implement step
    });
    then('Mavenir creates a ++Mavenir customer++', () => {
      // TODO: implement step
    })
      .and('Mavenir returns the ++Mavenir customer++ id', () => {
        // TODO: implement step
      });
  });

  scenario('Email already has a Mavenir Customer', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('no ++Mavenir customer++ for that email', () => {
        // TODO: implement step
      })
        .and('Mavenir has that ++account token++ on the create request', () => {
          // TODO: implement step
        });
    });
    given('Mavenir has a ++Mavenir customer++ for that email', () => {
      // TODO: implement step
    });
    when('Mavenir is asked to create a ++Mavenir customer++ for that email', () => {
      // TODO: implement step
    });
    then('Mavenir returns a conflict', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Store Mavenir Customer Id on Cognito User
 */

story('Store Mavenir Customer Id on Cognito User', () => {
  scenario('Store Mavenir Customer Id on Cognito User', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('My Paradise has added a ++Mavenir customer++ through the Midtier', () => {
        // TODO: implement step
      })
        .and('that add returned a ++Mavenir customer++ id', () => {
          // TODO: implement step
        });
    });
    when('My Paradise has a ++Mavenir customer++ id from the Midtier', () => {
      // TODO: implement step
    });
    then('My Paradise stores the ++Mavenir customer++ id on the ++Cognito user++ routing through Amplify to Cognito', () => {
      // TODO: implement step
    })
      .and('My Paradise proceeds to load the ++My Paradise customer++ from Midtier', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Load My Paradise Customer From Midtier And Store In Session
 */

story('Load My Paradise Customer From Midtier And Store In Session', () => {
  scenario('Load My Paradise Customer From Midtier And Store In Session', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the browser session has an ++account token++', () => {
        // TODO: implement step
      })
        .and('the ++Cognito user++ has a ++Mavenir customer++ id', () => {
          // TODO: implement step
        })
        .and('the ++My Paradise customer++ is not in session', () => {
          // TODO: implement step
        });
    });
    when('the User proceeds to Account Setup or My Paradise', () => {
      // TODO: implement step
    });
    then('My Paradise retrieves the ++Mavenir customer++ through the Midtier', () => {
      // TODO: implement step
    })
      .and('My Paradise stores the ++My Paradise customer++ in session', () => {
        // TODO: implement step
      });
  });

  scenario('Billing account is terminated', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the browser session has an ++account token++', () => {
        // TODO: implement step
      })
        .and('the ++Cognito user++ has a ++Mavenir customer++ id', () => {
          // TODO: implement step
        })
        .and('the ++My Paradise customer++ is not in session', () => {
          // TODO: implement step
        });
    });
    given('the ++Mavenir customer++ billing state is terminated', () => {
      // TODO: implement step
    });
    when('the User proceeds to Account Setup or My Paradise', () => {
      // TODO: implement step
    });
    then('My Paradise signs the User out', () => {
      // TODO: implement step
    })
      .and('My Paradise shows the terminated-account message', () => {
        // TODO: implement step
      });
  });

  scenario('Load customer fails', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the browser session has an ++account token++', () => {
        // TODO: implement step
      })
        .and('the ++Cognito user++ has a ++Mavenir customer++ id', () => {
          // TODO: implement step
        })
        .and('the ++My Paradise customer++ is not in session', () => {
          // TODO: implement step
        });
    });
    when('the User proceeds to Account Setup or My Paradise', () => {
      // TODO: implement step
    });
    then('My Paradise signs the User out', () => {
      // TODO: implement step
    })
      .and('My Paradise shows *Something went wrong when loading your account*', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Get Mavenir Customer and Transform To My Paradise Customer And Return
 */

story('Get Mavenir Customer and Transform To My Paradise Customer And Return', () => {
  scenario('Get Mavenir Customer and Transform To My Paradise Customer And Return', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('Midtier has verified the ++account token++', () => {
        // TODO: implement step
      })
        .and('the ++account token++ has a ++Mavenir customer++ id', () => {
          // TODO: implement step
        })
        .and('Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)', () => {
          // TODO: implement step
        });
    });
    when('Midtier receives a Paradise request to get a ++PML customer++', () => {
      // TODO: implement step
    });
    then('Midtier maps that request to a Mavenir customerDetails get for the ++Mavenir customer++ ++new Mavenir customer++', () => {
      // TODO: implement step
    })
      .and('Midtier submits customerDetails to Mavenir', () => {
        // TODO: implement step
      })
      .and('Midtier receives the ++Mavenir customer++ ++new Mavenir customer++', () => {
        // TODO: implement step
      })
      .and('Midtier maps that ++Mavenir customer++ to a new ++PML customer++', () => {
        // TODO: implement step
      })
      .and('Midtier returns the new ++PML customer++', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Get Mavenir Customer
 */

story('Get Mavenir Customer', () => {
  scenario('Get Mavenir Customer', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)', () => {
        // TODO: implement step
      });
    });
    when('Mavenir is asked to get the ++Mavenir customer++', () => {
      // TODO: implement step
    });
    then('Mavenir returns the ++Mavenir customer++ ++new Mavenir customer++', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Ensure Cart on Customer
 */

story('Ensure Cart on Customer', () => {
  // TODO: add main-flow scenario
});

/**
 * Story: Fix Orphan Cognito Account
 */

story('Fix Orphan Cognito Account', () => {
  scenario('Fix Orphan Cognito Account', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('the User has clicked Create account with ++account credentials++ ++valid account credentials++', () => {
        // TODO: implement step
      })
        .and('Cognito has an ++Cognito user++ ++unconfirmed Cognito user++', () => {
          // TODO: implement step
        })
        .but('the User has not entered a ++validation code++', () => {
          // TODO: implement step
        })
        .and('no ++account token++ is issued', () => {
          // TODO: implement step
        });
    });
    when('Care is asked to fix the orphan ++Cognito user++', () => {
      // TODO: implement step
    });
    then('Care changes the email in Mavenir DEP', () => {
      // TODO: implement step
    })
      .and('Care does not delete the ++Cognito user++', () => {
        // TODO: implement step
      });
  });

});

/**
 * Story: Read False Initial Activation
 */

story('Read False Initial Activation', () => {
  scenario('Read False Initial Activation', ({ given, when, then }) => {
    background('background', ({ given }) => {
      given('Mavenir has a ++Mavenir customer++', () => {
        // TODO: implement step
      })
        .and('that ++Mavenir customer++ has a ++Mavenir shopping cart++', () => {
          // TODO: implement step
        })
        .but('that ++Mavenir customer++ has no ++billing account++', () => {
          // TODO: implement step
        });
    });
    when('Care is asked to read the ++Mavenir customer++ in DEP', () => {
      // TODO: implement step
    });
    then('Care sees Initial Activation', () => {
      // TODO: implement step
    });
  });

});

/**
 * Story: Sign In With Existing Account
 */

story('Sign In With Existing Account', () => {
  scenario('Sign in with already-registered account credentials', ({ given, when, then }) => {
    given('Cognito has ++Cognito user++ ++already-registered Cognito user++', () => {
      // TODO: implement step
    })
      .and('the Customer is not signed in', () => {
        // TODO: implement step
      })
      .and('the Customer has ++account credentials++ ++already-registered account credentials++', () => {
        // TODO: implement step
      });
    when('the Customer authenticates ++account credentials++ ++already-registered account credentials++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // TODO: implement step
    });
    when('Cognito authenticates the account and issues an ++account token++', () => {
      // TODO: implement step
    });
    then('My Paradise stores ++Cognito user++ ++signed-in Cognito user++', () => {
      // TODO: implement step
    })
      .and('the Cognito user has the Mavenir customer id', () => {
        // TODO: implement step
      });
  });

  scenario('Email format is unmet', ({ given, when, then }) => {
    given('the Customer has ++account credentials++ ++invalid email format++', () => {
      // TODO: implement step
    });
    when('the Customer authenticates ++account credentials++ ++invalid email format++', () => {
      // TODO: implement step
    });
    then('My Paradise does not send a sign-in request to Cognito', () => {
      // TODO: implement step
    })
      .and('the authentication is rejected', () => {
        // TODO: implement step
      })
      .and('Cognito does not issue an ++account token++', () => {
        // TODO: implement step
      });
  });

  scenario('Authenticate with incorrect account credentials', ({ given, when, then }) => {
    given('Cognito has ++Cognito user++ ++already-registered Cognito user++', () => {
      // TODO: implement step
    })
      .and('the Customer has ++account credentials++ {example}', () => {
        // TODO: implement step
      });
    when('the Customer authenticates ++account credentials++ {example}', () => {
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // TODO: implement step
    });
    when('Cognito returns ++NotAuthorizedException++', () => {
      // TODO: implement step
    });
    then('the authentication is rejected', () => {
      // TODO: implement step
    })
      .and('Cognito does not issue an ++account token++', () => {
        // TODO: implement step
      });
  });

  scenario('Authenticate with unconfirmed account', ({ given, when, then }) => {
    given('Cognito has ++Cognito user++ ++unconfirmed Cognito user++', () => {
      // TODO: implement step
    });
    when('the Customer authenticates ++account credentials++ ++unconfirmed sign-in++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // TODO: implement step
    });
    when('Cognito returns ++CONFIRM_SIGN_UP++', () => {
      // TODO: implement step
    });
    then('the authentication is rejected as unconfirmed', () => {
      // TODO: implement step
    })
      .and('Cognito does not issue an ++account token++', () => {
        // TODO: implement step
      });
  });

  scenario('Password reset required', ({ given, when, then }) => {
    given('Cognito has ++Cognito user++ ++already-registered Cognito user++', () => {
      // TODO: implement step
    })
      .and('Cognito requires a password reset for ++already-registered account credentials++', () => {
        // TODO: implement step
      })
      .and('the Customer has ++account credentials++ ++already-registered account credentials++', () => {
        // TODO: implement step
      });
    when('the Customer authenticates ++account credentials++ ++already-registered account credentials++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // TODO: implement step
    });
    when('Cognito returns ++PasswordResetRequiredException++', () => {
      // TODO: implement step
    });
    then('the authentication requires a password reset', () => {
      // TODO: implement step
    })
      .and('Cognito does not issue an ++account token++', () => {
        // TODO: implement step
      });
  });

  scenario('New password required', ({ given, when, then }) => {
    given('Cognito has ++Cognito user++ ++already-registered Cognito user++', () => {
      // TODO: implement step
    })
      .and('Cognito requires a new password for ++already-registered account credentials++', () => {
        // TODO: implement step
      })
      .and('the Customer has ++account credentials++ ++already-registered account credentials++', () => {
        // TODO: implement step
      });
    when('the Customer authenticates ++account credentials++ ++already-registered account credentials++', () => {
      // TODO: implement step
    });
    then('My Paradise sends the sign-in request to Cognito', () => {
      // TODO: implement step
    });
    when('Cognito returns ++CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED++', () => {
      // TODO: implement step
    });
    then('the authentication requires a new password', () => {
      // TODO: implement step
    })
      .and('Cognito does not issue an ++account token++', () => {
        // TODO: implement step
      });
  });

});
