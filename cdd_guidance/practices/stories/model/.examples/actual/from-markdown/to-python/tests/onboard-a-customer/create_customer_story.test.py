from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Create Customer
# Orders: 0.0.1

# Story: Enter Account Credentials
# background-examples: {"email required": {"account credential requirements": "account credential requirements", "example": "email required", "field": "email", "requirement": "Email is required", "group": "Account credential requirements"}, "email format": {"account credential requirements": "account credential requirements", "example": "email format", "field": "email", "requirement": "Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com)", "group": "Account credential requirements"}, "password letters": {"account credential requirements": "account credential requirements", "example": "password letters", "field": "password", "requirement": "Password must contain uppercase and lowercase letters", "group": "Account credential requirements"}, "password number": {"account credential requirements": "account credential requirements", "example": "password number", "field": "password", "requirement": "Password must have at least one number", "group": "Account credential requirements"}, "password symbol": {"account credential requirements": "account credential requirements", "example": "password symbol", "field": "password", "requirement": "Password must have at least one symbol", "group": "Account credential requirements"}, "password length": {"account credential requirements": "account credential requirements", "example": "password length", "field": "password", "requirement": "Length must be greater than 8 characters", "group": "Account credential requirements"}, "confirm required": {"account credential requirements": "account credential requirements", "example": "confirm required", "field": "confirmPassword", "requirement": "Confirm Password is required", "group": "Account credential requirements"}, "confirm mismatch": {"account credential requirements": "account credential requirements", "example": "confirm mismatch", "field": "confirmPassword", "requirement": "Passwords don't match", "group": "Account credential requirements"}, "example": {"account credential requirements": "account credentials", "example": "example", "field": "unmet", "requirement": "Create account", "group": "Account credential requirements"}, "valid account credentials": {"account credential requirements": "account credentials", "example": "valid account credentials", "field": "", "requirement": "enabled", "group": "Account credential requirements"}, "Paradise Mobile account credentials": {"account credential requirements": "account credentials", "example": "Paradise Mobile account credentials", "field": "", "requirement": "enabled", "group": "Account credential requirements"}, "invalid password letters": {"account credential requirements": "account credentials", "example": "invalid password letters", "field": "Password must contain uppercase and lowercase letters", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password number": {"account credential requirements": "account credentials", "example": "invalid password number", "field": "Password must have at least one number", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password symbol": {"account credential requirements": "account credentials", "example": "invalid password symbol", "field": "Password must have at least one symbol", "requirement": "disabled", "group": "Account credential requirements"}, "invalid password length": {"account credential requirements": "account credentials", "example": "invalid password length", "field": "Length must be greater than 8 characters", "requirement": "disabled", "group": "Account credential requirements"}, "invalid confirm required": {"account credential requirements": "account credentials", "example": "invalid confirm required", "field": "Confirm Password is required", "requirement": "disabled", "group": "Account credential requirements"}, "invalid confirm mismatch": {"account credential requirements": "account credentials", "example": "invalid confirm mismatch", "field": "Passwords don't match", "requirement": "disabled", "group": "Account credential requirements"}, "invalid email required": {"account credential requirements": "account credentials", "example": "invalid email required", "field": "Email is required", "requirement": "disabled", "group": "Account credential requirements"}, "invalid email format": {"account credential requirements": "account credentials", "example": "invalid email format", "field": "Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com)", "requirement": "disabled", "group": "Account credential requirements"}}
with story("Enter Account Credentials"):
    with background.background:
        with scenario("Enter new account credentials"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            # background-step: And | the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
            with when("the User proceeds to create an account from the Paradise Mobile website"):
                pass
            with then("the User can enter ++account credentials++"):
                pass
            with and_("++account credential requirements++ are shown in black (Email is required, password rules)"):
                pass
            with and_("the Create account operation is disabled"):
                pass
            with and_("the User can Sign in"):
                pass
            with and_("the User can go Back"):
                pass
            with and_("the User can open Service Agreement, Terms and Conditions, and Privacy Policy"):
                pass
            with when("the User validates ++account credentials++ {example}"):
                pass
            with then("++account credentials++ are validated continuously as the User types"):
                pass
            with and_("unmet ++account credential requirements++ {unmet} are red with ✖"):
                pass
            with and_("the Create account button is {Create account}"):
                pass
            with when("the User clicks on Create account"):
                pass
            with then("the system creates an unconfirmed Cognito user routing through Amplify to Cognito"):
                pass
            with and_("the User is forwarded to check their email"):
                pass
        with scenario("Paradise Mobile email"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            # background-step: And | the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
            with when("the User enters ++account credentials++ ++Paradise Mobile account credentials++"):
                pass
            with then("the Create Account title is blue"):
                pass
        with scenario("Email already registered"):
            # background: background
            # background-step: Given | the plan catalog contains purchasable plans
            # background-step: And | the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site
            with given("++account credentials++ ++already-registered account credentials++ are already registered"):
                pass
            with when("the User registers ++account credentials++ ++already-registered account credentials++"):
                pass
            with then("Email shows the already-registered error"):
                pass

# Story: Create Unconfirmed Cognito User
with story("Create Unconfirmed Cognito User"):
        with scenario("Create Unconfirmed Cognito User"):
            # background: background
            # background-step: Given | no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
            with when("Cognito is asked to register ++account credentials++ ++valid account credentials++"):
                pass
            with then("Cognito creates ++Cognito user++ ++unconfirmed Cognito user++"):
                pass
            with and_("Cognito emails a ++validation code++ for those ++account credentials++"):
                pass
            with but_("no ++account token++ is issued"):
                pass
            with but_("no ++Mavenir customer++ exists for those ++account credentials++"):
                pass
        with scenario("Email already registered in Cognito"):
            # background: background
            # background-step: Given | no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++
            with given("++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++"):
                pass
            with when("Cognito is asked to register ++account credentials++ ++already-registered account credentials++"):
                pass
            with then("Cognito returns ++UsernameExistsException++"):
                pass
            with and_("Cognito does not create another ++Cognito user++ for those ++account credentials++"):
                pass
        with scenario("Cognito register fails with another error"):
            # background: background
            # background-step: Given | no ++Cognito user++ exists for ++account credentials++ ++valid account credentials++

# Story: Enter Validation Code
# Actor: My Paradise
# background-examples: {"valid validation code": {"validation code": "validation code", "example": "valid validation code", "code": "123456", "group": "validation code"}, "mismatch validation code": {"validation code": "validation code", "example": "mismatch validation code", "code": "Hmm. That code didn't work.", "group": "validation code"}, "expired validation code": {"validation code": "validation code", "example": "expired validation code", "code": "Hmm. That code didn't work.", "group": "validation code"}, "attempts exceeded validation code": {"validation code": "validation code", "example": "attempts exceeded validation code", "code": "Attempts limit exceeded. Please try again later.", "group": "validation code"}, "example": {"validation code": "validation code", "example": "example", "code": "helper", "group": "validation code"}}
with story("Enter Validation Code"):
    with background.background:
        with scenario("Enter validation code"):
            # background: background
            # background-step: Given | the User has submitted ++account credentials++ ++valid account credentials++
            # background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
            with when("the User proceeds to check their email"):
                pass
            with then("the User sees the code was sent to *[Jeff.anderson@Abdworks.com](mailto:Jeff.anderson@Abdworks.com)*"):
                pass
            with and_("the User can enter a ++validation code++ in Enter Validation Code"):
                pass
            with and_("the User can Resend"):
                pass
            with and_("the User can Close"):
                pass
            with and_("the Activate account operation is disabled"):
                pass
            with when("the User enters a ++validation code++ ++valid validation code++"):
                pass
            with then("the Activate account operation is enabled"):
                pass
            with when("the User clicks Activate account"):
                pass
            with then("the system confirms the ++Cognito user++ routing through Amplify to Cognito"):
                pass
            with and_("the User is forwarded to onboarding"):
                pass
        with scenario("Activate with unusable validation code"):
            # background: background
            # background-step: Given | the User has submitted ++account credentials++ ++valid account credentials++
            # background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
            with when("the User clicks Activate account with ++validation code++ {scenario}"):
                pass
            with then("Enter Validation Code shows helper text {helper}"):
                pass
        with scenario("Resend validation code"):
            # background: background
            # background-step: Given | the User has submitted ++account credentials++ ++valid account credentials++
            # background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
            with when("the User clicks Resend"):
                pass
            with then("the system emails a new ++validation code++ routing through Amplify to Cognito"):
                pass
            with and_("the User sees *We sent you a new code. Please check your email.*"):
                pass
            with and_("Resend waits 60 seconds before it can be used again"):
                pass

# Story: Confirm Cognito User
# background-examples: {"mismatch validation code": {"validation code": "validation code", "example": "mismatch validation code", "error": "CodeMismatchException"}, "expired validation code": {"validation code": "validation code", "example": "expired validation code", "error": "ExpiredCodeException"}, "attempts exceeded validation code": {"validation code": "validation code", "example": "attempts exceeded validation code", "error": "LimitExceededException"}}
with story("Confirm Cognito User"):
    with background.background:
        with scenario("Confirm Cognito User"):
            # background: background
            # background-step: Given | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
            with when("Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++"):
                pass
            with then("Cognito confirms the ++Cognito user++"):
                pass
            with but_("no ++account token++ is issued"):
                pass
            with but_("no ++Mavenir customer++ exists for those ++account credentials++"):
                pass
        with scenario("Confirm with unusable validation code"):
            # background: background
            # background-step: Given | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
            with when("Cognito is asked to confirm the user with ++validation code++ {scenario}"):
                pass
            with then("Cognito returns {error}"):
                pass
            with and_("Cognito does not confirm the ++Cognito user++"):
                pass

# Story: Issue Account Token To Browser Session
with story("Issue Account Token To Browser Session"):
        with scenario("Issue Account Token To Browser Session"):
            # background: background
            # background-step: Given | Cognito has a ++Cognito user++ ++confirmed Cognito user++
            with when("Cognito is asked to authenticate ++account credentials++ ++valid account credentials++"):
                pass
            with then("Cognito issues an ++account token++ for the ++Cognito user++"):
                pass
            with but_("no ++Mavenir customer++ exists for those ++account credentials++"):
                pass

# Story: Validate Mavenir Customer in Cognito User Attributes
with story("Validate Mavenir Customer in Cognito User Attributes"):
        with scenario("Cognito User already has a Mavenir Customer id"):
            # background: background
            # background-step: Given | the User is in Account Setup
            # background-step: And | Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++
            with given("the ++Cognito user++ has a ++Mavenir customer++ id"):
                pass
            with when("the User proceeds to Account Setup"):
                pass
            with then("My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito"):
                pass
            with and_("My Paradise finds the ++Mavenir customer++ id on the ++Cognito user++"):
                pass
            with and_("My Paradise proceeds to load the ++My Paradise customer++ from Midtier"):
                pass
        with scenario("Cognito User has no Mavenir Customer id"):
            # background: background
            # background-step: Given | the User is in Account Setup
            # background-step: And | Cognito has issued an ++account token++ for ++account credentials++ ++valid account credentials++
            with but_("no ++Mavenir customer++ exists for those ++account credentials++"):
                pass
            with when("the User proceeds to Account Setup"):
                pass
            with then("My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito"):
                pass
            with and_("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass

# Story: Submit Create Customer Request to Mid-Tier
with story("Submit Create Customer Request to Mid-Tier"):
        with scenario("Submit Create Customer Request to Mid-Tier"):
            # background: background
            # background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
            # background-step: And | the browser session has an ++account token++
            with when("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass
            with then("My Paradise adds a ++Mavenir customer++ through the Midtier"):
                pass
        with scenario("Email already has a Mavenir Customer"):
            # background: background
            # background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
            # background-step: And | the browser session has an ++account token++
            with given("a ++Mavenir customer++ already exists for that email"):
                pass
            with when("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass
            with then("My Paradise shows *Could not create customer.*"):
                pass
        with scenario("Invalid Account Token"):
            # background: background
            # background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
            # background-step: And | the browser session has an ++account token++
            with given("the ++account token++ is invalid"):
                pass
            with when("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass
            with then("My Paradise shows *Could not create customer.*"):
                pass
        with scenario("Mavenir is unreachable"):
            # background: background
            # background-step: Given | the ++Cognito user++ has no ++Mavenir customer++ id
            # background-step: And | the browser session has an ++account token++
            with given("Mavenir has no HTTP response"):
                pass
            with when("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass
            with then("My Paradise shows *Could not create customer.*"):
                pass

# Story: Validate Cognito User
with story("Validate Cognito User"):
        with scenario("Validate Cognito User"):
            # background: background
            # background-step: Given | the User has an ++account token++
            with when("Midtier is asked to validate the ++account token++"):
                pass
            with then("Midtier verifies the ++account token++"):
                pass
            with and_("Midtier reads the email from the ++account token++"):
                pass
            with when("the ++account token++ is invalid"):
                pass
            with then("Midtier returns \"Invalid token\""):
                pass

# Story: Submit Create Mavenir Customer
with story("Submit Create Mavenir Customer"):
        with scenario("Submit Create Mavenir Customer"):
            # background: background
            # background-step: Given | Midtier has verified the ++account token++
            # background-step: And | the ++account token++ has an email
            with when("Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++"):
                pass
            with then("Midtier maps that request to a Mavenir createaccounts for a ++Mavenir customer++ (email and ++contact medium++ from that email)"):
                pass
            with and_("Midtier submits createaccounts to Mavenir"):
                pass
            with and_("Midtier receives a Mavenir createaccounts response with the ++Mavenir customer++ id"):
                pass
            with and_("Midtier maps that ++Mavenir customer++ id to a ++PML customer++ id"):
                pass
            with and_("Midtier returns the ++PML customer++ id"):
                pass
        with scenario("Mavenir customer already exists"):
            # background: background
            # background-step: Given | Midtier has verified the ++account token++
            # background-step: And | the ++account token++ has an email
            with given("a ++Mavenir customer++ already exists for that email"):
                pass
            with when("Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++"):
                pass
            with then("Midtier receives a Mavenir createaccounts conflict"):
                pass
            with and_("Midtier maps that conflict to Paradise 409"):
                pass
            with and_("Midtier returns 409"):
                pass
        with scenario("Mavenir is unreachable"):
            # background: background
            # background-step: Given | Midtier has verified the ++account token++
            # background-step: And | the ++account token++ has an email
            with given("Mavenir has no HTTP response"):
                pass
            with when("Midtier receives a Paradise request to create a ++PML customer++ with the email from the ++account token++"):
                pass
            with then("Midtier maps that missing response to Paradise 504"):
                pass
            with and_("Midtier returns 504"):
                pass

# Story: Create Customer
# Actor: My Paradise
with story("Create Customer"):
        with scenario("Create Customer"):
            # background: background
            # background-step: Given | no ++Mavenir customer++ for that email
            # background-step: And | Mavenir has that ++account token++ on the create request
            with when("Mavenir is asked to create a ++Mavenir customer++ for that email"):
                pass
            with then("Mavenir creates a ++Mavenir customer++"):
                pass
            with and_("Mavenir returns the ++Mavenir customer++ id"):
                pass
        with scenario("Email already has a Mavenir Customer"):
            # background: background
            # background-step: Given | no ++Mavenir customer++ for that email
            # background-step: And | Mavenir has that ++account token++ on the create request
            with given("Mavenir has a ++Mavenir customer++ for that email"):
                pass
            with when("Mavenir is asked to create a ++Mavenir customer++ for that email"):
                pass
            with then("Mavenir returns a conflict"):
                pass

# Story: Store Mavenir Customer Id on Cognito User
with story("Store Mavenir Customer Id on Cognito User"):
        with scenario("Store Mavenir Customer Id on Cognito User"):
            # background: background
            # background-step: Given | My Paradise has added a ++Mavenir customer++ through the Midtier
            # background-step: And | that add returned a ++Mavenir customer++ id
            with when("My Paradise has a ++Mavenir customer++ id from the Midtier"):
                pass
            with then("My Paradise stores the ++Mavenir customer++ id on the ++Cognito user++ routing through Amplify to Cognito"):
                pass
            with and_("My Paradise proceeds to load the ++My Paradise customer++ from Midtier"):
                pass

# Story: Load My Paradise Customer From Midtier And Store In Session
with story("Load My Paradise Customer From Midtier And Store In Session"):
        with scenario("Load My Paradise Customer From Midtier And Store In Session"):
            # background: background
            # background-step: Given | the browser session has an ++account token++
            # background-step: And | the ++Cognito user++ has a ++Mavenir customer++ id
            # background-step: And | the ++My Paradise customer++ is not in session
            with when("the User proceeds to Account Setup or My Paradise"):
                pass
            with then("My Paradise retrieves the ++Mavenir customer++ through the Midtier"):
                pass
            with and_("My Paradise stores the ++My Paradise customer++ in session"):
                pass
        with scenario("Billing account is terminated"):
            # background: background
            # background-step: Given | the browser session has an ++account token++
            # background-step: And | the ++Cognito user++ has a ++Mavenir customer++ id
            # background-step: And | the ++My Paradise customer++ is not in session
            with given("the ++Mavenir customer++ billing state is terminated"):
                pass
            with when("the User proceeds to Account Setup or My Paradise"):
                pass
            with then("My Paradise signs the User out"):
                pass
            with and_("My Paradise shows the terminated-account message"):
                pass
        with scenario("Load customer fails"):
            # background: background
            # background-step: Given | the browser session has an ++account token++
            # background-step: And | the ++Cognito user++ has a ++Mavenir customer++ id
            # background-step: And | the ++My Paradise customer++ is not in session
            with when("the User proceeds to Account Setup or My Paradise"):
                pass
            with then("My Paradise signs the User out"):
                pass
            with and_("My Paradise shows *Something went wrong when loading your account*"):
                pass

# Story: Get Mavenir Customer and Transform To My Paradise Customer And Return
with story("Get Mavenir Customer and Transform To My Paradise Customer And Return"):
        with scenario("Get Mavenir Customer and Transform To My Paradise Customer And Return"):
            # background: background
            # background-step: Given | Midtier has verified the ++account token++
            # background-step: And | the ++account token++ has a ++Mavenir customer++ id
            # background-step: And | Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)
            with when("Midtier receives a Paradise request to get a ++PML customer++"):
                pass
            with then("Midtier maps that request to a Mavenir customerDetails get for the ++Mavenir customer++ ++new Mavenir customer++"):
                pass
            with and_("Midtier submits customerDetails to Mavenir"):
                pass
            with and_("Midtier receives the ++Mavenir customer++ ++new Mavenir customer++"):
                pass
            with and_("Midtier maps that ++Mavenir customer++ to a new ++PML customer++"):
                pass
            with and_("Midtier returns the new ++PML customer++"):
                pass

# Story: Get Mavenir Customer
with story("Get Mavenir Customer"):
        with scenario("Get Mavenir Customer"):
            # background: background
            # background-step: Given | Mavenir has a new Mavenir customer (`++new Mavenir customer++` row)
            with when("Mavenir is asked to get the ++Mavenir customer++"):
                pass
            with then("Mavenir returns the ++Mavenir customer++ ++new Mavenir customer++"):
                pass

# Story: Fix Orphan Cognito Account
with story("Fix Orphan Cognito Account"):
        with scenario("Fix Orphan Cognito Account"):
            # background: background
            # background-step: Given | the User has clicked Create account with ++account credentials++ ++valid account credentials++
            # background-step: And | Cognito has an ++Cognito user++ ++unconfirmed Cognito user++
            # background-step: But | the User has not entered a ++validation code++
            # background-step: And | no ++account token++ is issued
            with when("Care is asked to fix the orphan ++Cognito user++"):
                pass
            with then("Care changes the email in Mavenir DEP"):
                pass
            with and_("Care does not delete the ++Cognito user++"):
                pass

# Story: Read False Initial Activation
with story("Read False Initial Activation"):
        with scenario("Read False Initial Activation"):
            # background: background
            # background-step: Given | Mavenir has a ++Mavenir customer++
            # background-step: And | that ++Mavenir customer++ has a ++Mavenir shopping cart++
            # background-step: But | that ++Mavenir customer++ has no ++billing account++
            with when("Care is asked to read the ++Mavenir customer++ in DEP"):
                pass
            with then("Care sees Initial Activation"):
                pass

# Story: Sign In With Existing Account
with story("Sign In With Existing Account"):
        with scenario("Sign in with already-registered account credentials"):
            with given("Cognito has ++Cognito user++ ++already-registered Cognito user++"):
                pass
            with and_("the Customer is not signed in"):
                pass
            with and_("the Customer has ++account credentials++ ++already-registered account credentials++"):
                pass
            with when("the Customer authenticates ++account credentials++ ++already-registered account credentials++"):
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                pass
            with when("Cognito authenticates the account and issues an ++account token++"):
                pass
            with then("My Paradise stores ++Cognito user++ ++signed-in Cognito user++"):
                pass
            with and_("the Cognito user has the Mavenir customer id"):
                pass
        with scenario("Email format is unmet"):
            with given("the Customer has ++account credentials++ ++invalid email format++"):
                pass
            with when("the Customer authenticates ++account credentials++ ++invalid email format++"):
                pass
            with then("My Paradise does not send a sign-in request to Cognito"):
                pass
            with and_("the authentication is rejected"):
                pass
            with and_("Cognito does not issue an ++account token++"):
                pass
        with scenario("Authenticate with incorrect account credentials"):
            with given("Cognito has ++Cognito user++ ++already-registered Cognito user++"):
                pass
            with and_("the Customer has ++account credentials++ {example}"):
                pass
            with when("the Customer authenticates ++account credentials++ {example}"):
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                pass
            with when("Cognito returns ++NotAuthorizedException++"):
                pass
            with then("the authentication is rejected"):
                pass
            with and_("Cognito does not issue an ++account token++"):
                pass
        with scenario("Authenticate with unconfirmed account"):
            with given("Cognito has ++Cognito user++ ++unconfirmed Cognito user++"):
                pass
            with when("the Customer authenticates ++account credentials++ ++unconfirmed sign-in++"):
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                pass
            with when("Cognito returns ++CONFIRM_SIGN_UP++"):
                pass
            with then("the authentication is rejected as unconfirmed"):
                pass
            with and_("Cognito does not issue an ++account token++"):
                pass
        with scenario("Password reset required"):
            with given("Cognito has ++Cognito user++ ++already-registered Cognito user++"):
                pass
            with and_("Cognito requires a password reset for ++already-registered account credentials++"):
                pass
            with and_("the Customer has ++account credentials++ ++already-registered account credentials++"):
                pass
            with when("the Customer authenticates ++account credentials++ ++already-registered account credentials++"):
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                pass
            with when("Cognito returns ++PasswordResetRequiredException++"):
                pass
            with then("the authentication requires a password reset"):
                pass
            with and_("Cognito does not issue an ++account token++"):
                pass
        with scenario("New password required"):
            with given("Cognito has ++Cognito user++ ++already-registered Cognito user++"):
                pass
            with and_("Cognito requires a new password for ++already-registered account credentials++"):
                pass
            with and_("the Customer has ++account credentials++ ++already-registered account credentials++"):
                pass
            with when("the Customer authenticates ++account credentials++ ++already-registered account credentials++"):
                pass
            with then("My Paradise sends the sign-in request to Cognito"):
                pass
            with when("Cognito returns ++CONFIRM_SIGN_IN_WITH_NEW_PASSWORD_REQUIRED++"):
                pass
            with then("the authentication requires a new password"):
                pass
            with and_("Cognito does not issue an ++account token++"):
                pass
