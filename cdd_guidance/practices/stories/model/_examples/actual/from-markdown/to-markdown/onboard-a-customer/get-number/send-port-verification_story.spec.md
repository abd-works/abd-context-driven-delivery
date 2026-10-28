## Story: Send Port Verification

### Scenario: Send port verification SMS

*Given* `porting-2fa` is enabled
*And* ++portability++ ++valid portability++ is in the ++Mavenir shopping cart++
*When* Midtier sends port verification to ++portability++ ++valid portability++ portNumber
*Then* Midtier initiates a Twilio SMS verification to ++portability++ ++valid portability++ portNumber
*And* Midtier returns `{ status: sent, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise

### Scenario: Send port verification — rate limited

*Given* `porting-2fa` is enabled
*When* Midtier sends port verification
*But* Twilio rate limits the request
*Then* Midtier returns `{ status: rate_limited, canBypass: true, temporaryNumber: ++available number++ ++held available number++ }` to My Paradise

### Scenario: Send port verification — invalid number

*Given* `porting-2fa` is enabled
*When* Midtier sends port verification
*But* Twilio rejects the number as invalid
*Then* Midtier returns `{ status: invalid_number }` to My Paradise
