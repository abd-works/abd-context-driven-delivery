---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Create Unconfirmed User

#### Scenario: Display Create Account

*When* the User proceeds to create an account from the Paradise Mobile website  
*Then* the User can enter [account credentials](../../../../domain/domain-model.md#accountcredentials-value-object)  
  *But* the email and password rules are unmet  
  *But* the customer cannot save the [customer account](../../../../domain/domain-model.md#customeraccount-aggregate-root-entity)

#### Scenario: Enter Valid account credentials

*When* the User enters valid [account credentials](../../../../domain/domain-model.md#accountcredentials-value-object)  
*Then* [account credentials](../../../../domain/domain-model.md#accountcredentials-value-object) are validated continuously  
  *And* the customer can save the [customer account](../../../../domain/domain-model.md#customeraccount-aggregate-root-entity)

#### Scenario: Enter Invalid account credentials: ${example}

*When* the User registers When the requirements have not been met  
*Then* the account cannot be registered  
  *And* the ${unmet} requirement is unmet  
  *And* the System displays the unmet requirements*

#### Scenario: Email already registered

*Given* already-registered [account credentials](../../../../domain/domain-model.md#accountcredentials-value-object) are already registered  
*When* the User registers already-registered [account credentials](../../../../domain/domain-model.md#accountcredentials-value-object)  
*Then* the email is already registered  
*And* The system displays a message that the account is already registered

#### Scenario: Create Unconfirmed User

*Given* the amplifyService.signUp spy is set up  
*When* the User creates their account  
*Then* the system creates an unconfirmed Cognito user and emails a validation code
