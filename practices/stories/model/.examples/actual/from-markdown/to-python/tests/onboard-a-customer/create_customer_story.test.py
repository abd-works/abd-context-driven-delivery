from __future__ import annotations

from story_test import and_, background, given, scenario, story, then, when

# Epic: Create Customer

# Story: Enter Account Credentials
with story("Enter Account Credentials"):
    with background.each:
        with scenario("Enter new account credentials"):
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
            with when("the User enters ++account credentials++ ++Paradise Mobile account credentials++"):
                pass
            with then("the Create Account title is blue"):
                pass
        with scenario("Email already registered"):
            with given("++account credentials++ ++already-registered account credentials++ are already registered"):
                pass
            with when("the User registers ++account credentials++ ++already-registered account credentials++"):
                pass
            with then("Email shows the already-registered error"):
                pass

# Story: Create Unconfirmed Cognito User
with story("Create Unconfirmed Cognito User"):
    with background.each:
        with scenario("Create Unconfirmed Cognito User"):
            with when("Cognito is asked to register ++account credentials++ ++valid account credentials++"):
                pass
            with then("Cognito creates ++Cognito user++ ++unconfirmed Cognito user++"):
                pass
            with and_("Cognito emails a ++validation code++ for those ++account credentials++"):
                pass
            with and_("no ++account token++ is issued"):
                pass
            with and_("no ++Mavenir customer++ exists for those ++account credentials++"):
                pass
        with scenario("Email already registered in Cognito"):
            with given("++Cognito user++ ++unconfirmed Cognito user++ exists for ++account credentials++ ++already-registered account credentials++"):
                pass
            with when("Cognito is asked to register ++account credentials++ ++already-registered account credentials++"):
                pass
            with then("Cognito returns ++UsernameExistsException++"):
                pass
            with and_("Cognito does not create another ++Cognito user++ for those ++account credentials++"):
                pass
        with scenario("Cognito register fails with another error"):
            pass

# Story: Enter Validation Code
# Actor: My Paradise
with story("Enter Validation Code"):
    with background.each:
        with scenario("Enter validation code"):
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
            with when("the User clicks Activate account with ++validation code++ {scenario}"):
                pass
            with then("Enter Validation Code shows helper text {helper}"):
                pass
        with scenario("Resend validation code"):
            with when("the User clicks Resend"):
                pass
            with then("the system emails a new ++validation code++ routing through Amplify to Cognito"):
                pass
            with and_("the User sees *We sent you a new code. Please check your email.*"):
                pass
            with and_("Resend waits 60 seconds before it can be used again"):
                pass

# Story: Confirm Cognito User
with story("Confirm Cognito User"):
    with background.each:
        with scenario("Confirm Cognito User"):
            with when("Cognito is asked to confirm the user with a ++validation code++ ++valid validation code++"):
                pass
            with then("Cognito confirms the ++Cognito user++"):
                pass
            with and_("no ++account token++ is issued"):
                pass
            with and_("no ++Mavenir customer++ exists for those ++account credentials++"):
                pass
        with scenario("Confirm with unusable validation code"):
            with when("Cognito is asked to confirm the user with ++validation code++ {scenario}"):
                pass
            with then("Cognito returns {error}"):
                pass
            with and_("Cognito does not confirm the ++Cognito user++"):
                pass

# Story: Issue Account Token To Browser Session
with story("Issue Account Token To Browser Session"):
    with background.each:
        with scenario("Issue Account Token To Browser Session"):
            with when("Cognito is asked to authenticate ++account credentials++ ++valid account credentials++"):
                pass
            with then("Cognito issues an ++account token++ for the ++Cognito user++"):
                pass
            with and_("no ++Mavenir customer++ exists for those ++account credentials++"):
                pass

# Story: Validate Mavenir Customer in Cognito User Attributes
with story("Validate Mavenir Customer in Cognito User Attributes"):
    with background.each:
        with scenario("Cognito User already has a Mavenir Customer id"):
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
            with then("no ++Mavenir customer++ exists for those ++account credentials++"):
                pass
            with when("the User proceeds to Account Setup"):
                pass
            with then("My Paradise reads the ++Cognito user++ attributes routing through Amplify to Cognito"):
                pass
            with and_("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass

# Story: Submit Create Customer Request to Mid-Tier
with story("Submit Create Customer Request to Mid-Tier"):
    with background.each:
        with scenario("Submit Create Customer Request to Mid-Tier"):
            with when("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass
            with then("My Paradise adds a ++Mavenir customer++ through the Midtier"):
                pass
        with scenario("Email already has a Mavenir Customer"):
            with given("a ++Mavenir customer++ already exists for that email"):
                pass
            with when("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass
            with then("My Paradise shows *Could not create customer.*"):
                pass
        with scenario("Invalid Account Token"):
            with given("the ++account token++ is invalid"):
                pass
            with when("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass
            with then("My Paradise shows *Could not create customer.*"):
                pass
        with scenario("Mavenir is unreachable"):
            with given("Mavenir has no HTTP response"):
                pass
            with when("My Paradise finds no ++Mavenir customer++ id on the ++Cognito user++"):
                pass
            with then("My Paradise shows *Could not create customer.*"):
                pass

# Story: Validate Cognito User
with story("Validate Cognito User"):
    with background.each:
        with scenario("Validate Cognito User"):
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
    with background.each:
        with scenario("Submit Create Mavenir Customer"):
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
    with background.each:
        with scenario("Create Customer"):
            with when("Mavenir is asked to create a ++Mavenir customer++ for that email"):
                pass
            with then("Mavenir creates a ++Mavenir customer++"):
                pass
            with and_("Mavenir returns the ++Mavenir customer++ id"):
                pass
        with scenario("Email already has a Mavenir Customer"):
            with given("Mavenir has a ++Mavenir customer++ for that email"):
                pass
            with when("Mavenir is asked to create a ++Mavenir customer++ for that email"):
                pass
            with then("Mavenir returns a conflict"):
                pass

# Story: Store Mavenir Customer Id on Cognito User
with story("Store Mavenir Customer Id on Cognito User"):
    with background.each:
        with scenario("Store Mavenir Customer Id on Cognito User"):
            with when("My Paradise has a ++Mavenir customer++ id from the Midtier"):
                pass
            with then("My Paradise stores the ++Mavenir customer++ id on the ++Cognito user++ routing through Amplify to Cognito"):
                pass
            with and_("My Paradise proceeds to load the ++My Paradise customer++ from Midtier"):
                pass

# Story: Load My Paradise Customer From Midtier And Store In Session
with story("Load My Paradise Customer From Midtier And Store In Session"):
    with background.each:
        with scenario("Load My Paradise Customer From Midtier And Store In Session"):
            with when("the User proceeds to Account Setup or My Paradise"):
                pass
            with then("My Paradise retrieves the ++Mavenir customer++ through the Midtier"):
                pass
            with and_("My Paradise stores the ++My Paradise customer++ in session"):
                pass
        with scenario("Billing account is terminated"):
            with given("the ++Mavenir customer++ billing state is terminated"):
                pass
            with when("the User proceeds to Account Setup or My Paradise"):
                pass
            with then("My Paradise signs the User out"):
                pass
            with and_("My Paradise shows the terminated-account message"):
                pass
        with scenario("Load customer fails"):
            with when("the User proceeds to Account Setup or My Paradise"):
                pass
            with then("My Paradise signs the User out"):
                pass
            with and_("My Paradise shows *Something went wrong when loading your account*"):
                pass

# Story: Get Mavenir Customer and Transform To My Paradise Customer And Return
with story("Get Mavenir Customer and Transform To My Paradise Customer And Return"):
    with background.each:
        with scenario("Get Mavenir Customer and Transform To My Paradise Customer And Return"):
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
    with background.each:
        with scenario("Get Mavenir Customer"):
            with when("Mavenir is asked to get the ++Mavenir customer++"):
                pass
            with then("Mavenir returns the ++Mavenir customer++ ++new Mavenir customer++"):
                pass

# Story: Fix Orphan Cognito Account
with story("Fix Orphan Cognito Account"):
    with background.each:
        with scenario("Fix Orphan Cognito Account"):
            with when("Care is asked to fix the orphan ++Cognito user++"):
                pass
            with then("Care changes the email in Mavenir DEP"):
                pass
            with and_("Care does not delete the ++Cognito user++"):
                pass

# Story: Read False Initial Activation
with story("Read False Initial Activation"):
    with background.each:
        with scenario("Read False Initial Activation"):
            with when("Care is asked to read the ++Mavenir customer++ in DEP"):
                pass
            with then("Care sees Initial Activation"):
                pass

# Story: Sign In With Existing Account
with story("Sign In With Existing Account"):
    with background.each:
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
