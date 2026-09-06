# clarify-domain-service-is-a-rare-doer

- **tool:** Ddd
- **error:** Credentials (a form/value) grew signIn/register/signOut. The agent “fixed anemic” by parking session verbs on the form, or would have invented an SOA `AuthenticationService`.
- **rule:** service-is-homeless, flaccid-data-object-no-behavior (existing pair — they fought)
- **what changed:**
  - **Prose — yes.** `context_tools/ddd/ddd.md`: Service row and `service-is-homeless` — a DDD Service is a **rare doer**, only when the operation will not sit cleanly on one domain object; not SOA `FooService`. If Customer signs in, that is `Customer.signIn`. `flaccid-data-object-no-behavior` — a type is not a field bag; it gets **its** work; credentials does not grow `signIn`.
  - **Sketch — yes.** Same two bullets on `context_tools/ddd/templates/ddd-sketch.md`.
  - **Detector — no.** Not a new named rule or scanner.
  - **Generator — no.**
