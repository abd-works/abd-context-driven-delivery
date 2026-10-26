## Story: Enter Account Credentials

### Examples

#### Account credential requirements

| account credential requirements | example | field | requirement | group |
| --- | --- | --- | --- | --- |
| account credential requirements | email required | email | Email is required | Account credential requirements |
| account credential requirements | email format | email | Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com) | Account credential requirements |
| account credential requirements | password letters | password | Password must contain uppercase and lowercase letters | Account credential requirements |
| account credential requirements | password number | password | Password must have at least one number | Account credential requirements |
| account credential requirements | password symbol | password | Password must have at least one symbol | Account credential requirements |
| account credential requirements | password length | password | Length must be greater than 8 characters | Account credential requirements |
| account credential requirements | confirm required | confirmPassword | Confirm Password is required | Account credential requirements |
| account credential requirements | confirm mismatch | confirmPassword | Passwords don't match | Account credential requirements |
| account credentials | example | unmet | Create account | Account credential requirements |
| account credentials | valid account credentials |  | enabled | Account credential requirements |
| account credentials | Paradise Mobile account credentials |  | enabled | Account credential requirements |
| account credentials | invalid password letters | Password must contain uppercase and lowercase letters | disabled | Account credential requirements |
| account credentials | invalid password number | Password must have at least one number | disabled | Account credential requirements |
| account credentials | invalid password symbol | Password must have at least one symbol | disabled | Account credential requirements |
| account credentials | invalid password length | Length must be greater than 8 characters | disabled | Account credential requirements |
| account credentials | invalid confirm required | Confirm Password is required | disabled | Account credential requirements |
| account credentials | invalid confirm mismatch | Passwords don't match | disabled | Account credential requirements |
| account credentials | invalid email required | Email is required | disabled | Account credential requirements |
| account credentials | invalid email format | Please use a valid email format: [yourname@domain.com](mailto:yourname@domain.com) | disabled | Account credential requirements |

### Scenario Outline: Enter new account credentials

### Background

*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site

*When* the User proceeds to create an account from the Paradise Mobile website
*Then* the User can enter ++account credentials++
*And* ++account credential requirements++ are shown in black (Email is required, password rules)
*And* the Create account operation is disabled
*And* the User can Sign in
*And* the User can go Back
*And* the User can open Service Agreement, Terms and Conditions, and Privacy Policy
*When* the User validates ++account credentials++ {example}
*Then* ++account credentials++ are validated continuously as the User types
*And* unmet ++account credential requirements++ {unmet} are red with ✖
*And* the Create account button is {Create account}
*When* the User clicks on Create account
*Then* the system creates an unconfirmed Cognito user routing through Amplify to Cognito
*And* the User is forwarded to check their email

### Scenario: Paradise Mobile email

### Background

*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site

*When* the User enters ++account credentials++ ++Paradise Mobile account credentials++
*Then* the Create Account title is blue

### Scenario: Email already registered

### Background

*Given* the plan catalog contains purchasable plans
*And* the User has selected ++plan++ ++Essentials++ on the Paradise Mobile site

*Given* ++account credentials++ ++already-registered account credentials++ are already registered
*When* the User registers ++account credentials++ ++already-registered account credentials++
*Then* Email shows the already-registered error
