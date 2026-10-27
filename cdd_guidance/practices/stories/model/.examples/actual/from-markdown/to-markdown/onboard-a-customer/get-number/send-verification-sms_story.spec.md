## Story: Send Verification Sms

### Scenario: Send verification SMS

*Given* `porting-2fa` is enabled
*And* ++portability++ ++valid portability++ portNumber is a valid Bermuda number
*When* Twilio is asked to send a verification SMS to ++portability++ ++valid portability++ portNumber
*Then* Twilio creates a verification for ++portability++ ++valid portability++ portNumber (`channel: sms`)
*And* Twilio returns `sent` to Midtier

### Scenario: Send verification SMS — rate limited

*Given* `porting-2fa` is enabled
*When* Twilio is asked to send a verification SMS
*But* the rate limit for ++portability++ ++valid portability++ portNumber is exceeded
*Then* Twilio returns `rate_limited` to Midtier
