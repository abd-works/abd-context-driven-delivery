/**
 * Epic: Create Customer
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Enter Account Credentials
 */

story('Enter Account Credentials', () => {
  background('each', ({ given }) => {
    scenario('Enter new account credentials', ({ given, when, then }) => {
      when('the User proceeds to create an account from the Paradise Mobile website', () => {});
      then('the User can enter ++account credentials++', () => {}).and('++account credential requirements++ are shown in black (Email is required, password rules)', () => {}).and('the Create account operation is disabled', () => {}).and('the User can Sign in', () => {}).and('the User can go Back', () => {}).and('the User can open Service Agreement, Terms and Conditions, and Privacy Policy', () => {});
      when('the User validates ++account credentials++ {example}', () => {});
      then('++account credentials++ are validated continuously as the User types', () => {}).and('unmet ++account credential requirements++ {unmet} are red with ✖', () => {}).and('the Create account button is {Create account}', () => {});
      when('the User clicks on Create account', () => {});
      then('the system creates an unconfirmed Cognito user routing through Amplify to Cognito', () => {}).and('the User is forwarded to check their email', () => {});
    });
    scenario('Paradise Mobile email', ({ given, when, then }) => {
      when('the User enters ++account credentials++ ++Paradise Mobile account credentials++', () => {});
      then('the Create Account title is blue', () => {});
    });
    scenario('Email already registered', ({ given, when, then }) => {
      given('++account credentials++ ++already-registered account credentials++ are already registered', () => {});
      when('the User registers ++account credentials++ ++already-registered account credentials++', () => {});
      then('Email shows the already-registered error', () => {});
    });
  });
});

/**
 * Story: Create Unconfirmed Cognito User
 */

story('Create Unconfirmed Cognito User', () => {
  background('each', ({ given }) => {
    scenario('Create Unconfirmed Cognito User', ({ given, when, then }) => {
      when('Cognito is asked to register ++account credentials++ ++valid account credentials++', () => {});
      then('Cognito creates ++Cognito user++ ++unconfirmed Cognito user++', () => {}).and('Cognito emails a ++validation code++ for those ++account credentials++', () => {}).but('no ++account token++ is issued', () => {}).but('no ++Mavenir customer++ exists for those ++account credentials++', () => {});
    });
    scenario('Email already registered in Cognito', ({ given, when, then }) => {
      given('++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++', () => {});
      when('Cognito is asked to register ++account credentials++ ++already-registered account credentials++', () => {});
      then('Cognito returns ++UsernameExistsException++', () => {}).and('Cognito does not create another ++Cognito user++ for those ++account credentials++', () => {});
    });
    scenario('Cognito register fails with another error', ({ given, when, then }) => {
    });
  });
});

/**
 * Story: Enter Validation Code
 * Actor: My Paradise
 */

story('Enter Validation Code', () => {
  background('each', ({ given }) => {
    scenario('Enter validation code', ({ given, when, then }) => {
      when('the User proceeds to check their email', () => {});
      then('the User sees the code was sent to [Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com)', () => {}).and('the User can enter a ++validation code++ in Enter Validation Code', () => {}).and('the User can Resend', () => {}).and('the User can Close', () => {}).and('the Activate account operation is disabled', () => {});
      when('the User enters a ++validation code++ ++valid validation code++', () => {});
      then('the Activate account operation is enabled', () => {});
      when('the User clicks Activate account', () => {});
      then('the system confirms the ++Cognito user++ routing through Amplify to Cognito', () => {}).and('the User is forwarded to onboarding', () => {});
    });
    scenario('Activate with unusable validation code', ({ given, when, then }) => {
      when('the User clicks Activate account with ++validation code++ {scenario}', () => {});
      then('Enter Validation Code shows helper text {helper}', () => {});
    });
    scenario('Resend validation code', ({ given, when, then }) => {
      when('the User clicks Resend', () => {});
      then('the system emails a new ++validation code++ routing through Amplify to Cognito', () => {}).and('the User sees We sent you a new code. Please check your email.', () => {}).and('Resend waits 60 seconds before it can be used again', () => {});
    });
  });
});

/**
 * Story: Confirm Cognito User
 */

story('Confirm Cognito User', () => {
  background('each', ({ given }) => {
    scenario('Confirm Cognito User', ({ given, when, then }) => {
      when('Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++', () => {});
      then('Cognito confirms the ++Cognito user++', () => {}).but('no ++account token++ is issued', () => {}).but('no ++Mavenir customer++ exists for those ++account credentials++', () => {});
    });
    scenario('Confirm with unusable validation code', ({ given, when, then }) => {
      when('Cognito is asked to confirm the user with ++validation code++ {scenario}', () => {});
      then('Cognito returns {error}', () => {}).and('Cognito does not confirm the ++Cognito user++', () => {});
    });
  });
});

/**
 * Story: Issue Account Token To Browser Session
 */

story('Issue Account Token To Browser Session', () => {
  background('each', ({ given }) => {
    scenario('Issue Account Token To Browser Session', ({ given, when, then }) => {
      when('Cognito is asked to authenticate ++account credentials++ ++valid account credentials++', () => {});
      then('Cognito issues an ++account token++ for the ++Cognito user++', () => {}).but('no ++Mavenir customer++ exists for those ++account credentials++', () => {});
    });
  });
});

/**
 * Story: Validate Mavenir Customer in Cognito User Attributes
 */

story('Validate Mavenir Customer in Cognito User Attributes', () => {
  background('each', ({ given }) => {
    scenario('Cognito User already has a Mavenir Customer id', ({ given, when, then }) => {
      given('the ++Cognito user++ has a ++Mavenir customer++ id', () => {});
      when('the User proceeds to Account Setup', () => {});
      then('My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito', () => {}).and('My Paradise finds the ++Mavenir customer++ id on the ++Cognito user++', () => {}).and('My Paradise proceeds to load the ++My Paradise customer++ from Midtier', () => {});
    });
    scenario('Cognito User has no Mavenir Customer id', ({ given, when, then }) => {
      then('no ++Mavenir customer++ exists for those ++account credentials++', () => {});
      when('the User proceeds to Account Setup', () => {});
      then('My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito', () => {}).and('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
    });
  });
});

/**
 * Story: Submit Create Customer Request to Mid-Tier
 */

story('Submit Create Customer Request to Mid-Tier', () => {
  background('each', ({ given }) => {
    scenario('Submit Create Customer Request to Mid-Tier', ({ given, when, then }) => {
      when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
      then('My Paradise adds a ++Mavenir customer++ through the Midtier', () => {});
    });
    scenario('Email already has a Mavenir Customer', ({ given, when, then }) => {
      given('a ++Mavenir customer++ already exists for that email', () => {});
      when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
      then('My Paradise shows Could not create customer.', () => {});
    });
    scenario('Invalid Account Token', ({ given, when, then }) => {
      given('the ++account token++ is invalid', () => {});
      when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
      then('My Paradise shows Could not create customer.', () => {});
    });
    scenario('Mavenir is unreachable', ({ given, when, then }) => {
      given('Mavenir has no HTTP response', () => {});
      when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
      then('My Paradise shows Could not create customer.', () => {});
    });
  });
});

/**
 * Story: Validate Cognito User
 */

story('Validate Cognito User', () => {
  background('each', ({ given }) => {
    scenario('Validate Cognito User', ({ given, when, then }) => {
      when('Midtier is asked to validate the ++account token++', () => {});
      then('Midtier verifies the ++account token++', () => {}).and('Midtier reads the email from the ++account token++', () => {});
      when('the ++account token++ is invalid', () => {});
      then('Midtier returns "Invalid token"', () => {});
    });
  });
});

/**
 * Story: Submit Create Mavenir Customer
 */

story('Submit Create Mavenir Customer', () => {
  background('each', ({ given }) => {
    scenario('Submit Create Mavenir Customer', ({ given, when, then }) => {
      when('Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++', () => {});
      then('Midtier maps that request to a Mavenir createaccounts for a ++Mavenir customer++ (email and ++contact medium++ from that email)', () => {}).and('Midtier submits createaccounts to Mavenir', () => {}).and('Midtier receives a Mavenir createaccounts response with the ++Mavenir customer++ id', () => {}).and('Midtier maps that ++Mavenir customer++ id to a ++PML customer++ id', () => {}).and('Midtier returns the ++PML customer++ id', () => {});
    });
    scenario('Mavenir customer already exists', ({ given, when, then }) => {
      given('a ++Mavenir customer++ already exists for that email', () => {});
      when('Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++', () => {});
      then('Midtier receives a Mavenir createaccounts conflict', () => {}).and('Midtier maps that conflict to Paradise 409', () => {}).and('Midtier returns 409', () => {});
    });
    scenario('Mavenir is unreachable', ({ given, when, then }) => {
      given('Mavenir has no HTTP response', () => {});
      when('Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++', () => {});
      then('Midtier maps that missing response to Paradise 504', () => {}).and('Midtier returns 504', () => {});
    });
  });
});

/**
 * Story: Create Customer
 * Actor: My Paradise
 */

story('Create Customer', () => {
  background('each', ({ given }) => {
    scenario('Create Customer', ({ given, when, then }) => {
      when('Mavenir is asked to create a ++Mavenir customer++ for that email', () => {});
      then('Mavenir creates a ++Mavenir customer++', () => {}).and('Mavenir returns the ++Mavenir customer++ id', () => {});
    });
    scenario('Email already has a Mavenir Customer', ({ given, when, then }) => {
      given('Mavenir has a ++Mavenir customer++ for that email', () => {});
      when('Mavenir is asked to create a ++Mavenir customer++ for that email', () => {});
      then('Mavenir returns a conflict', () => {});
    });
  });
});

/**
 * Story: Store Mavenir Customer Id on Cognito User
 */

story('Store Mavenir Customer Id on Cognito User', () => {
  background('each', ({ given }) => {
    scenario('Store Mavenir Customer Id on Cognito User', ({ given, when, then }) => {
      when('My Paradise has a ++Mavenir customer++ id from the Midtier', () => {});
      then('My Paradise stores the ++Mavenir customer++ id on the ++Cognito user++ routing through Amplify to Cognito', () => {}).and('My Paradise proceeds to load the ++My Paradise customer++ from Midtier', () => {});
    });
  });
});

/**
 * Story: Load My Paradise Customer From Midtier And Store In Session
 */

story('Load My Paradise Customer From Midtier And Store In Session', () => {
  background('each', ({ given }) => {
    scenario('Load My Paradise Customer From Midtier And Store In Session', ({ given, when, then }) => {
      when('the User proceeds to Account Setup or My Paradise', () => {});
      then('My Paradise retrieves the ++Mavenir customer++ through the Midtier', () => {}).and('My Paradise stores the ++My Paradise customer++ in session', () => {});
    });
    scenario('Billing account is terminated', ({ given, when, then }) => {
      given('the ++Mavenir customer++ billing state is terminated', () => {});
      when('the User proceeds to Account Setup or My Paradise', () => {});
      then('My Paradise signs the User out', () => {}).and('My Paradise shows the terminated-account message', () => {});
    });
    scenario('Load customer fails', ({ given, when, then }) => {
      when('the User proceeds to Account Setup or My Paradise', () => {});
      then('My Paradise signs the User out', () => {}).and('My Paradise shows Something went wrong when loading your account', () => {});
    });
  });
});

/**
 * Story: Get Mavenir Customer and Transform To My Paradise Customer And Return
 */

story('Get Mavenir Customer and Transform To My Paradise Customer And Return', () => {
  background('each', ({ given }) => {
    scenario('Get Mavenir Customer and Transform To My Paradise Customer And Return', ({ given, when, then }) => {
      when('Midtier receives a Paradise request to get a ++PML customer++', () => {});
      then('Midtier maps that request to a Mavenir customerDetails get for the ++Mavenir customer++ ++new Mavenir customer++', () => {}).and('Midtier submits customerDetails to Mavenir', () => {}).and('Midtier receives the ++Mavenir customer++ ++new Mavenir customer++', () => {}).and('Midtier maps that ++Mavenir customer++ to a new ++PML customer++', () => {}).and('Midtier returns the new ++PML customer++', () => {});
    });
  });
});

/**
 * Story: Get Mavenir Customer
 */

story('Get Mavenir Customer', () => {
  background('each', ({ given }) => {
    scenario('Get Mavenir Customer', ({ given, when, then }) => {
      when('Mavenir is asked to get the ++Mavenir customer++', () => {});
      then('Mavenir returns the ++Mavenir customer++ ++new Mavenir customer++', () => {});
    });
  });
});

/**
 * Story: Fix Orphan Cognito Account
 */

story('Fix Orphan Cognito Account', () => {
  background('each', ({ given }) => {
    scenario('Fix Orphan Cognito Account', ({ given, when, then }) => {
      when('Care is asked to fix the orphan ++Cognito user++', () => {});
      then('Care changes the email in Mavenir DEP', () => {}).and('Care does not delete the ++Cognito user++', () => {});
    });
  });
});

/**
 * Story: Read False Initial Activation
 */

story('Read False Initial Activation', () => {
  background('each', ({ given }) => {
    scenario('Read False Initial Activation', ({ given, when, then }) => {
      when('Care is asked to read the ++Mavenir customer++ in DEP', () => {});
      then('Care sees Initial Activation', () => {});
    });
  });
});

/**
 * Story: Sign In With Existing Account
 */

story('Sign In With Existing Account', () => {
  background('each', ({ given }) => {
    scenario('Sign in with already-registered account credentials', ({ given, when, then }) => {
      given('Cognito has ++Cognito user++ ++already-registered Cognito user++', () => {}).and('the Customer is not signed in', () => {}).and('the Customer has ++account credentials++ ++already-registered account credentials++', () => {});
      when('the Customer authenticates ++account credentials++ ++already-registered account credentials++', () => {});
      then('My Paradise sends the sign-in request to Cognito', () => {});
      when('Cognito authenticates the account and issues an ++account token++', () => {});
      then('My Paradise stores ++Cognito user++ ++signed-in Cognito user++', () => {}).and('the Cognito user has the Mavenir customer id', () => {});
    });
    scenario('Email format is unmet', ({ given, when, then }) => {
      given('the Customer has ++account credentials++ ++invalid email format++', () => {});
      when('the Customer authenticates ++account credentials++ ++invalid email format++', () => {});
      then('My Paradise does not send a sign-in request to Cognito', () => {}).and('the authentication is rejected', () => {}).and('Cognito does not issue an ++account token++', () => {});
    });
    scenario('Authenticate with incorrect account credentials', ({ given, when, then }) => {
      given('Cognito has ++Cognito user++ ++already-registered Cognito user++', () => {}).and('the Customer has ++account credentials++ {example}', () => {});
      when('the Customer authenticates ++account credentials++ {example}', () => {});
      then('My Paradise sends the sign-in request to Cognito', () => {});
      when('Cognito returns ++NotAuthorizedException++', () => {});
      then('the authentication is rejected', () => {}).and('Cognito does not issue an ++account token++', () => {});
    });
    scenario('Authenticate with unconfirmed account', ({ given, when, then }) => {
      given('Cognito has ++Cognito user++ ++unconfirmed Cognito user++', () => {});
      when('the Customer authenticates ++account credentials++ ++unconfirmed sign-in++', () => {});
      then('My Paradise sends the sign-in request to Cognito', () => {});
      when('Cognito returns ++CONFIRM_SIGN_UP++', () => {});
      then('the authentication is rejected as unconfirmed', () => {}).and('Cognito does not issue an ++account token++', () => {});
    });
    scenario('Password reset required', ({ given, when, then }) => {
      given('Cognito has ++Cognito user++ ++already-registered Cognito user++', () => {}).and('Cognito requires a password reset for ++already-registered account credentials++', () => {}).and('the Customer has ++account credentials++ ++already-registered account credentials++', () => {});
      when('the Customer authenticates ++account credentials++ ++already-registered account credentials++', () => {});
      then('My Paradise sends the sign-in request to Cognito', () => {});
      when('Cognito returns ++PasswordResetRequiredException++', () => {});
      then('the authentication requires a password reset', () => {}).and('Cognito does not issue an ++account token++', () => {});
    });
    scenario('New password required', ({ given, when, then }) => {
      given('Cognito has ++Cognito user++ ++already-registered Cognito user++', () => {}).and('Cognito requires a new password for ++already-registered account credentials++', () => {}).and('the Customer has ++account credentials++ ++already-registered account credentials++', () => {});
      when('the Customer authenticates ++account credentials++ ++already-registered account credentials++', () => {});
      then('My Paradise sends the sign-in request to Cognito', () => {});
      when('Cognito returns ++CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED++', () => {});
      then('the authentication requires a new password', () => {}).and('Cognito does not issue an ++account token++', () => {});
    });
  });
});
