# Rule: Stub service interaction belongs in GIVEN and WHEN, never split across WHEN/THEN

When an external integration (microservice, third-party API, downstream system) is **stubbed**, its request payload and response are **hardcoded** — the outcome is not observable, it is a precondition. Structure the scenario accordingly.

## Pattern

**GIVEN** — declare the stub: the service name, the hardcoded request it expects, and the hardcoded response it returns. This is configuration state, not behavior.

**WHEN** — express the full observable interaction as a sequence:
- the system captures or receives the triggering input
- the system forwards or invokes the stubbed service with the fixed request
- the stubbed service returns the fixed response

**THEN** — assert the business outcome only. Never assert what a stubbed service returns; that is already fixed in GIVEN.

## DO

```gherkin
Given *PaymentGateway* is stubbed to receive charge request for *$120.00 AUD* and return *transaction-id: TXN-9912, status: approved*
When the *Checkout* captures *order #4471* with total *$120.00 AUD*
  And the *Checkout* forwards the charge request to *PaymentGateway*
  And *PaymentGateway* returns *transaction-id: TXN-9912, status: approved*
Then the *Order #4471* status is *Paid*
  And the *Transaction* *TXN-9912* is recorded against *Order #4471*
```

Multiple stubs in one scenario:

```gherkin
Given *IdentityService* is stubbed to receive token *tok-abc* and return *user-id: U-44, roles: [member]*
  And *NotificationService* is stubbed to receive *welcome email* for *user U-44* and return *sent: true*
When the *SignIn* captures authentication request with token *tok-abc*
  And the *SignIn* invokes *IdentityService* with token *tok-abc*
  And *IdentityService* returns *user-id: U-44, roles: [member]*
  And the *SignIn* invokes *NotificationService* with *welcome email* for *user U-44*
  And *NotificationService* returns *sent: true*
Then the *Session* is created for *user U-44*
```

## DON'T

Do **not** split a stub interaction across WHEN/THEN beats as though the service response is a business outcome:

```gherkin
# WRONG — stub response in THEN is not a business outcome
When the system invokes *PaymentGateway*
Then *PaymentGateway* returns *approved*
Then *Order #4471* status is *Paid*
```

Do **not** omit the stub declaration from GIVEN:

```gherkin
# WRONG — where does approved come from? The stub is invisible
When the system charges *$120.00 AUD*
Then the *Order* is *Paid*
```

Do **not** put the stub invocation alone in WHEN and leave the response implicit:

```gherkin
# WRONG — response never stated, scenario is incomplete
When the *Checkout* invokes *PaymentGateway*
Then the *Order* is *Paid*
```

## Stub data table

When a scenario uses a stubbed service, record the input/output pair in the scenario's **stub data table** (if the spec uses one) and add the same values to the project's stub fixture files. See rule `sync-stub-data-with-scenarios` in `abd-story-acceptance-test`.
