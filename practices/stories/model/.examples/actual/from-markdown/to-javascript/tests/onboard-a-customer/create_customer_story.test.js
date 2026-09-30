/**
 * Epic: Create Customer
 * Orders: 0.0.1
 */

import { background, scenario, story } from "../story-test.js";

/**
 * Story: Enter Account Credentials
 */

// background-examples: {"email required": {"account credential requirements": "account credential requirements", "example": "email required", "field": "email", "requirement": "Email is required", "group": "Account credential requirements"}, "email format": {"account credential requirements": "account credential requirements", "example": "email format", "field": "email", "requirement": "Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com)", "group": "Account credential requirements"}, "password letters": {"account credential requirements": "account credential requirements", "example": "password letters", "field": "password", "requirement": "Password must contain uppercase and lowercase letters", "group": "Account credential requirements"}, "password number": {"account credential requirements": "account credential requirements", "example": "password number", "field": "password", "requirement": "Password must have at least one number", "group": "Account credential requirements"}, "password symbol": {"account credential requirements": "account credential requirements", "example": "password symbol", "field": "password", "requirement": "Password must have at least one symbol", "group": "Account credential requirements"}, "password length": {"account credential requirements": "account credential requirements", "example": "password length", "field": "password", "requirement": "Length must be greater than 8 characters", "group": "Account credential requirements"}, "confirm required": {"account credential requirements": "account credential requirements", "example": "confirm required", "field": "confirmPassword", "requirement": "Confirm Password is required", "group": "Account credential requirements"}, "confirm mismatch": {"account credential requirements": "account credential requirements", "example": "confirm mismatch", "field": "confirmPassword", "requirement": "Passwords don't match", "group": "Account credential requirements"}, "example": {"account credential requirements": "account credentials", "example": "example", "field": "unmet", "requirement": "Create account", "group": "Account credential requirements"}, "valid account credentials": {"account credential requirements": "account credentials", "example": "valid account credentials", "field": "", "requirement": "enabled", "group": "Account credential requirements"}, "Paradise Mobile account credentials": {"account credential requirements": "account credentials", "example": "Paradise Mobile account credentials", "field": "", "requirement": "enabled", "group": "Account credential requirements"}, "invalid password letters": {"account credential requirements": "account credentials", "example": "invalid password letters", "field": "Password must contain uppercase and lowercase letters", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password number": {"account credential requirements": "account credentials", "example": "invalid password number", "field": "Password must have at least one number", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password symbol": {"account credential requirements": "account credentials", "example": "invalid password symbol", "field": "Password must have at least one symbol", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password length": {"account credential requirements": "account credentials", "example": "invalid password length", "field": "Length must be greater than 8 characters", "requirement": "disabled", "group": "Account credential requirements"}, "invalid confirm required": {"account credential requirements": "account credentials", "example": "invalid confirm required", "field": "Confirm Password is required", "requirement": "disabled", "group": "Account credential requirements"}, "invalid confirm mismatch": {"account credential requirements": "account credentials", "example": "invalid confirm mismatch", "field": "Passwords don't match", "requirement": "disabled", "group": "Account credential requirements"}, "invalid email required": {"account credential requirements": "account credentials", "example": "invalid email required", "field": "Email is required", "requirement": "disabled", "group": "Account credential requirements"}, "invalid email format": {"account credential requirements": "account credentials", "example": "invalid email format", "field": "Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com)", "requirement": "disabled", "group": "Account credential requirements"}}
story('Enter Account Credentials', () => {
  background('background', ({ given }) => {
  });
    scenario('Enter new account credentials', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      // background-step: And | the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
      when('the User proceeds to create an account from the Paradise Mobile website', () => {});
      then('the User can enter ++account credentials++', () => {}).and('++account credential requirements++ are shown in black (Email is required, password rules)', () => {}).and('the Create account operation is disabled', () => {}).and('the User can Sign in', () => {}).and('the User can go Back', () => {}).and('the User can open Service Agreement, Terms and Conditions, and Privacy Policy', () => {});
      when('the User validates ++account credentials++ {example}', () => {});
      then('++account credentials++ are validated continuously as the User types', () => {}).and('unmet ++account credential requirements++ {unmet} are red with ✖', () => {}).and('the Create account button is {Create account}', () => {});
      when('the User clicks on Create account', () => {});
      then('the system creates an unconfirmed Cognito user routing through Amplify to Cognito', () => {}).and('the User is forwarded to check their email', () => {});
    });
    scenario('Paradise Mobile email', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      // background-step: And | the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
      when('the User enters ++account credentials++ ++Paradise Mobile account credentials++', () => {});
      then('the Create Account title is blue', () => {});
    });
    scenario('Email already registered', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the plan catalog contains purchasable plans
      // background-step: And | the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
      given('++account credentials++ ++already-registered account credentials++ are already registered', () => {});
      when('the User registers ++account credentials++ ++already-registered account credentials++', () => {});
      then('Email shows the already-registered error', () => {});
    });
});

/**
 * Story: Create Unconfirmed Cognito User
 */

story('Create Unconfirmed Cognito User', () => {
    scenario('Create Unconfirmed Cognito User', ({ given, when, then }) => {
      // background: background
      // background-step: Given | no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
      when('Cognito is asked to register ++account credentials++ ++valid account credentials++', () => {});
      then('Cognito creates ++Cognito user++ ++unconfirmed Cognito user++', () => {}).and('Cognito emails a ++validation code++ for those ++account credentials++', () => {}).but('no ++account token++ is issued', () => {}).but('no ++Mavenir customer++ exists for those ++account credentials++', () => {});
    });
    scenario('Email already registered in Cognito', ({ given, when, then }) => {
      // background: background
      // background-step: Given | no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
      given('++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++', () => {});
      when('Cognito is asked to register ++account credentials++ ++already-registered account credentials++', () => {});
      then('Cognito returns ++UsernameExistsException++', () => {}).and('Cognito does not create another ++Cognito user++ for those ++account credentials++', () => {});
    });
    scenario('Cognito register fails with another error', ({ given, when, then }) => {
      // background: background
      // background-step: Given | no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
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
      // background: background
      // background-step: Given | the User has submitted ++account credentials++ ++valid account credentials++
      // background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
      when('the User proceeds to check their email', () => {});
      then('the User sees the code was sent to *[Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com)*', () => {}).and('the User can enter a ++validation code++ in Enter Validation Code', () => {}).and('the User can Resend', () => {}).and('the User can Close', () => {}).and('the Activate account operation is disabled', () => {});
      when('the User enters a ++validation code++ ++valid validation code++', () => {});
      then('the Activate account operation is enabled', () => {});
      when('the User clicks Activate account', () => {});
      then('the system confirms the ++Cognito user++ routing through Amplify to Cognito', () => {}).and('the User is forwarded to onboarding', () => {});
    });
    scenario('Activate with unusable validation code', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the User has submitted ++account credentials++ ++valid account credentials++
      // background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
      when('the User clicks Activate account with ++validation code++ {scenario}', () => {});
      then('Enter Validation Code shows helper text {helper}', () => {});
    });
    scenario('Resend validation code', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the User has submitted ++account credentials++ ++valid account credentials++
      // background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
      when('the User clicks Resend', () => {});
      then('the system emails a new ++validation code++ routing through Amplify to Cognito', () => {}).and('the User sees *We sent you a new code. Please check your email.*', () => {}).and('Resend waits 60 seconds before it can be used again', () => {});
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
      // background: background
      // background-step: Given | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
      when('Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++', () => {});
      then('Cognito confirms the ++Cognito user++', () => {}).but('no ++account token++ is issued', () => {}).but('no ++Mavenir customer++ exists for those ++account credentials++', () => {});
    });
    scenario('Confirm with unusable validation code', ({ given, when, then }) => {
      // background: background
      // background-step: Given | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
      when('Cognito is asked to confirm the user with ++validation code++ {scenario}', () => {});
      then('Cognito returns {error}', () => {}).and('Cognito does not confirm the ++Cognito user++', () => {});
    });
});

/**
 * Story: Issue Account Token To Browser Session
 */

story('Issue Account Token To Browser Session', () => {
    scenario('Issue Account Token To Browser Session', ({ given, when, then }) => {
      // background: background
      // background-step: Given | Cognito has a ++Cognito user++ ++confirmed Cognito user++
      when('Cognito is asked to authenticate ++account credentials++ ++valid account credentials++', () => {});
      then('Cognito issues an ++account token++ for the ++Cognito user++', () => {}).but('no ++Mavenir customer++ exists for those ++account credentials++', () => {});
    });
});

/**
 * Story: Validate Mavenir Customer in Cognito User Attributes
 */

story('Validate Mavenir Customer in Cognito User Attributes', () => {
    scenario('Cognito User already has a Mavenir Customer id', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the User is in Account Setup
      // background-step: And | Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++
      given('the ++Cognito user++ has a ++Mavenir customer++ id', () => {});
      when('the User proceeds to Account Setup', () => {});
      then('My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito', () => {}).and('My Paradise finds the ++Mavenir customer++ id on the ++Cognito user++', () => {}).and('My Paradise proceeds to load the ++My Paradise customer++ from Midtier', () => {});
    });
    scenario('Cognito User has no Mavenir Customer id', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the User is in Account Setup
      // background-step: And | Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++
      but('no ++Mavenir customer++ exists for those ++account credentials++', () => {});
      when('the User proceeds to Account Setup', () => {});
      then('My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito', () => {}).and('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
    });
});

/**
 * Story: Submit Create Customer Request to Mid-Tier
 */

story('Submit Create Customer Request to Mid-Tier', () => {
    scenario('Submit Create Customer Request to Mid-Tier', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
      // background-step: And | the browser session has an ++account token++
      when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
      then('My Paradise adds a ++Mavenir customer++ through the Midtier', () => {});
    });
    scenario('Email already has a Mavenir Customer', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
      // background-step: And | the browser session has an ++account token++
      given('a ++Mavenir customer++ already exists for that email', () => {});
      when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
      then('My Paradise shows *Could not create customer.*', () => {});
    });
    scenario('Invalid Account Token', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
      // background-step: And | the browser session has an ++account token++
      given('the ++account token++ is invalid', () => {});
      when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
      then('My Paradise shows *Could not create customer.*', () => {});
    });
    scenario('Mavenir is unreachable', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
      // background-step: And | the browser session has an ++account token++
      given('Mavenir has no HTTP response', () => {});
      when('My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++', () => {});
      then('My Paradise shows *Could not create customer.*', () => {});
    });
});

/**
 * Story: Validate Cognito User
 */

story('Validate Cognito User', () => {
    scenario('Validate Cognito User', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the User has an ++account token++
      when('Midtier is asked to validate the ++account token++', () => {});
      then('Midtier verifies the ++account token++', () => {}).and('Midtier reads the email from the ++account token++', () => {});
      when('the ++account token++ is invalid', () => {});
      then('Midtier returns "Invalid token"', () => {});
    });
});

/**
 * Story: Submit Create Mavenir Customer
 */

story('Submit Create Mavenir Customer', () => {
    scenario('Submit Create Mavenir Customer', ({ given, when, then }) => {
      // background: background
      // background-step: Given | Midtier has verified the ++account token++
      // background-step: And | the ++account token++ has an email
      when('Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++', () => {});
      then('Midtier maps that request to a Mavenir createaccounts for a ++Mavenir customer++ (email and ++contact medium++ from that email)', () => {}).and('Midtier submits createaccounts to Mavenir', () => {}).and('Midtier receives a Mavenir createaccounts response with the ++Mavenir customer++ id', () => {}).and('Midtier maps that ++Mavenir customer++ id to a ++PML customer++ id', () => {}).and('Midtier returns the ++PML customer++ id', () => {});
    });
    scenario('Mavenir customer already exists', ({ given, when, then }) => {
      // background: background
      // background-step: Given | Midtier has verified the ++account token++
      // background-step: And | the ++account token++ has an email
      given('a ++Mavenir customer++ already exists for that email', () => {});
      when('Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++', () => {});
      then('Midtier receives a Mavenir createaccounts conflict', () => {}).and('Midtier maps that conflict to Paradise 409', () => {}).and('Midtier returns 409', () => {});
    });
    scenario('Mavenir is unreachable', ({ given, when, then }) => {
      // background: background
      // background-step: Given | Midtier has verified the ++account token++
      // background-step: And | the ++account token++ has an email
      given('Mavenir has no HTTP response', () => {});
      when('Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++', () => {});
      then('Midtier maps that missing response to Paradise 504', () => {}).and('Midtier returns 504', () => {});
    });
});

/**
 * Story: Create Customer
 * Actor: My Paradise
 */

story('Create Customer', () => {
    scenario('Create Customer', ({ given, when, then }) => {
      // background: background
      // background-step: Given | no ++Mavenir customer++ for that email
      // background-step: And | Mavenir has that ++account token++ on the create request
      when('Mavenir is asked to create a ++Mavenir customer++ for that email', () => {});
      then('Mavenir creates a ++Mavenir customer++', () => {}).and('Mavenir returns the ++Mavenir customer++ id', () => {});
    });
    scenario('Email already has a Mavenir Customer', ({ given, when, then }) => {
      // background: background
      // background-step: Given | no ++Mavenir customer++ for that email
      // background-step: And | Mavenir has that ++account token++ on the create request
      given('Mavenir has a ++Mavenir customer++ for that email', () => {});
      when('Mavenir is asked to create a ++Mavenir customer++ for that email', () => {});
      then('Mavenir returns a conflict', () => {});
    });
});

/**
 * Story: Store Mavenir Customer Id on Cognito User
 */

story('Store Mavenir Customer Id on Cognito User', () => {
    scenario('Store Mavenir Customer Id on Cognito User', ({ given, when, then }) => {
      // background: background
      // background-step: Given | My Paradise has added a ++Mavenir customer++ through the Midtier
      // background-step: And | that add returned a ++Mavenir customer++ id
      when('My Paradise has a ++Mavenir customer++ id from the Midtier', () => {});
      then('My Paradise stores the ++Mavenir customer++ id on the ++Cognito user++ routing through Amplify to Cognito', () => {}).and('My Paradise proceeds to load the ++My Paradise customer++ from Midtier', () => {});
    });
});

/**
 * Story: Load My Paradise Customer From Midtier And Store In Session
 */

story('Load My Paradise Customer From Midtier And Store In Session', () => {
    scenario('Load My Paradise Customer From Midtier And Store In Session', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the browser session has an ++account token++
      // background-step: And | the ++Cognito user++ has a ++Mavenir customer++ id
      // background-step: And | the ++My Paradise customer++ is not in session
      when('the User proceeds to Account Setup or My Paradise', () => {});
      then('My Paradise retrieves the ++Mavenir customer++ through the Midtier', () => {}).and('My Paradise stores the ++My Paradise customer++ in session', () => {});
    });
    scenario('Billing account is terminated', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the browser session has an ++account token++
      // background-step: And | the ++Cognito user++ has a ++Mavenir customer++ id
      // background-step: And | the ++My Paradise customer++ is not in session
      given('the ++Mavenir customer++ billing state is terminated', () => {});
      when('the User proceeds to Account Setup or My Paradise', () => {});
      then('My Paradise signs the User out', () => {}).and('My Paradise shows the terminated-account message', () => {});
    });
    scenario('Load customer fails', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the browser session has an ++account token++
      // background-step: And | the ++Cognito user++ has a ++Mavenir customer++ id
      // background-step: And | the ++My Paradise customer++ is not in session
      when('the User proceeds to Account Setup or My Paradise', () => {});
      then('My Paradise signs the User out', () => {}).and('My Paradise shows *Something went wrong when loading your account*', () => {});
    });
});

/**
 * Story: Get Mavenir Customer and Transform To My Paradise Customer And Return
 */

story('Get Mavenir Customer and Transform To My Paradise Customer And Return', () => {
    scenario('Get Mavenir Customer and Transform To My Paradise Customer And Return', ({ given, when, then }) => {
      // background: background
      // background-step: Given | Midtier has verified the ++account token++
      // background-step: And | the ++account token++ has a ++Mavenir customer++ id
      // background-step: And | Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)
      when('Midtier receives a Paradise request to get a ++PML customer++', () => {});
      then('Midtier maps that request to a Mavenir customerDetails get for the ++Mavenir customer++ ++new Mavenir customer++', () => {}).and('Midtier submits customerDetails to Mavenir', () => {}).and('Midtier receives the ++Mavenir customer++ ++new Mavenir customer++', () => {}).and('Midtier maps that ++Mavenir customer++ to a new ++PML customer++', () => {}).and('Midtier returns the new ++PML customer++', () => {});
    });
});

/**
 * Story: Get Mavenir Customer
 */

story('Get Mavenir Customer', () => {
    scenario('Get Mavenir Customer', ({ given, when, then }) => {
      // background: background
      // background-step: Given | Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)
      when('Mavenir is asked to get the ++Mavenir customer++', () => {});
      then('Mavenir returns the ++Mavenir customer++ ++new Mavenir customer++', () => {});
    });
});

/**
 * Story: Fix Orphan Cognito Account
 */

story('Fix Orphan Cognito Account', () => {
    scenario('Fix Orphan Cognito Account', ({ given, when, then }) => {
      // background: background
      // background-step: Given | the User has clicked Create account with ++account credentials++ ++valid account credentials++
      // background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
      // background-step: But | the User has not entered a ++validation code++
      // background-step: And | no ++account token++ is issued
      when('Care is asked to fix the orphan ++Cognito user++', () => {});
      then('Care changes the email in Mavenir DEP', () => {}).and('Care does not delete the ++Cognito user++', () => {});
    });
});

/**
 * Story: Read False Initial Activation
 */

story('Read False Initial Activation', () => {
    scenario('Read False Initial Activation', ({ given, when, then }) => {
      // background: background
      // background-step: Given | Mavenir has a ++Mavenir customer++
      // background-step: And | that ++Mavenir customer++ has a ++Mavenir shopping cart++
      // background-step: But | that ++Mavenir customer++ has no ++billing account++
      when('Care is asked to read the ++Mavenir customer++ in DEP', () => {});
      then('Care sees Initial Activation', () => {});
    });
});

/**
 * Story: Sign In With Existing Account
 */

story('Sign In With Existing Account', () => {
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
