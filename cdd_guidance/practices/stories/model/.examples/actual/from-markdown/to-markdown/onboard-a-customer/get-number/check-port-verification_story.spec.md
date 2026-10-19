## Story: Check Port Verification

### Scenario: Check port verification — code valid

### Background

*Given* a ++PML customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* a ++porting SMS code++ was sent to ++portability++ ++valid portability++ portNumber

*When* Midtier is asked to check ++porting SMS code++ ++valid porting SMS code++ against ++portability++ ++valid portability++ portNumber
*Then* Midtier checks the ++porting SMS code++ with Twilio
*And* Twilio returns `approved`
*And* Midtier marks the ++PML customer++ phone as verified
*And* Midtier returns `{ verified: true }` to My Paradise

### Scenario: Check port verification — code mismatch

### Background

*Given* a ++PML customer++ with a ++Mavenir shopping cart++
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*And* a ++porting SMS code++ was sent to ++portability++ ++valid portability++ portNumber

*When* Midtier is asked to check ++porting SMS code++ ++mismatch porting SMS code++ against ++portability++ ++valid portability++ portNumber
*Then* Midtier checks the ++porting SMS code++ with Twilio
*And* Twilio returns a non-approved status
*And* Midtier returns `{ verified: false }` to My Paradise
