---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
example-of: shared-example-fixtures
---

## Story: Enter Account Credentials

**Story type:** website

### Domain terms

- ++account credentials++ — email, password, confirm password; validated continuously on Create Account
- ++account credential requirements++ — live rule checklist on Create Account
- ++plan++ — sellable offering the User selects on the Telco Website
- ++identity provider user++ — pool user (unconfirmed until email is verified)

### Examples

#### account credentials

| account credentials | example | email | password | confirmPassword | Create account |
| --- | --- | --- | --- | --- | --- |
| account credentials | valid account credentials | prospect@example.com | Valid-pass99 | Valid-pass99 | enabled |
| account credentials | invalid password length | prospect@example.com | Sh0rt! | Sh0rt! | disabled |
| account credentials | invalid confirm mismatch | prospect@example.com | Valid-pass99 | Other-pass99 | disabled |

#### plan

| plan | example | id | name | monthlyPrice |
| --- | --- | --- | --- | --- |
| plan | Essentials | 100000000014 | Essentials | 70 |
| plan | Data Freedom | 100000000019 | Data Freedom | 55 |
| plan | Ace | 100000000042 | Ace | 99 |

#### identity provider user

| identity provider user | example | email | confirmed |
| --- | --- | --- | --- |
| identity provider user | unconfirmed identity provider user | prospect@example.com | no |

### Background

*Given* the plan catalog contains purchasable plans  
  *And* the User has selected ++plan++ ++Essentials++ on the Telco Website

### Behaviors

#### Scenario: Initial Create Account state

*When* the User proceeds to create an account from the Telco Website  
*Then* the User can enter ++account credentials++  
  *And* the email and password rules are unmet  
  *And* the Create account operation is disabled  
  *And* the User can Sign in  
  *And* the User can go Back

#### Scenario: Valid account credentials

*When* the User validates ++account credentials++ ++valid account credentials++  
*Then* ++account credentials++ are validated continuously  
  *And* the Create account operation is available  
*When* the User clicks on Create account  
*Then* the system creates an unconfirmed ++identity provider user++  
  *And* the User is forwarded to check their email

#### Scenario: Password too short

*When* the User validates ++account credentials++ ++invalid password length++  
*Then* the password length rule is unmet  
  *And* the Create account operation is disabled

#### Scenario: Confirm password mismatch

*When* the User validates ++account credentials++ ++invalid confirm mismatch++  
*Then* the confirm-password rule is unmet  
  *And* the Create account operation is disabled
