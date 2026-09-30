## Story: Check Verification

### Scenario: Check verification — code valid

### Background

*Given* a verification was sent to ++portability++ ++valid portability++ portNumber

*When* Twilio is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber
*Then* Twilio creates a verification check (`verificationChecks.create`)
*And* Twilio returns `approved` to Midtier

### Scenario: Check verification — code mismatch

### Background

*Given* a verification was sent to ++portability++ ++valid portability++ portNumber

*When* Twilio is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber
*Then* Twilio creates a verification check
*And* Twilio returns a non-approved status to Midtier
