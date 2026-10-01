---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Story: Create Unconfirmed User

#### Scenario: Create Unconfirmed User

*Given* the amplifyService.signUp spy is set up  
*When* the User creates their account  
*Then* the system creates an unconfirmed Cognito user and emails a validation code
