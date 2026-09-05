# Rule: Sync stub data with every scenario that uses it

When a test scenario invokes a stubbed external service, its hardcoded request/response pair is both **a test precondition** and **a permanent entry in the project's stub fixture data**. Every new scenario that exercises a different input/output combination must add that pair to the stub fixture so subsequent scenarios can rely on it.

## DO

**In the test:** configure the stub in `given_*` helpers with the exact request the system will send and the exact response the service will return.

**In the stub fixture file:** add a row (or entry) for each new request/response pair used by any scenario. The fixture grows with the spec.

```python
# given_* helper — hardcoded setup matches the spec's GIVEN step
def given_payment_gateway_stubbed(self, request_amount, response_body):
    self.stub_server.register(
        method="POST",
        path="/charge",
        request_body={"amount": request_amount},
        response=response_body,
    )

# test method — reads exactly like the spec scenario
def test_order_paid_on_approved_charge(self):
    self.given_payment_gateway_stubbed(
        request_amount="120.00 AUD",
        response_body={"transaction_id": "TXN-9912", "status": "approved"},
    )
    result = self.when_checkout_processes_order("order-4471", total="120.00 AUD")
    self.then_order_status_is(result, "Paid")
    self.then_transaction_recorded(result, transaction_id="TXN-9912")
```

**Stub fixture file** (e.g. `stubs/payment_gateway_stubs.json` or `stubs/handlers/payment-gateway.ts`):

```json
[
  { "request": { "amount": "120.00 AUD" }, "response": { "transaction_id": "TXN-9912", "status": "approved" } },
  { "request": { "amount": "0.00 AUD"  }, "response": { "error": "amount_zero" } }
]
```

Each row corresponds to a scenario in the spec. When you add a scenario, add the row.

## DON'T

Do **not** inline stub data only in the test without updating the fixture file:

```python
# WRONG — hardcoded only here; stubs/payment_gateway_stubs.json never updated
mock_gateway.return_value = {"status": "approved"}
```

Do **not** reuse a fixture row that was not written to match the new scenario's values:

```python
# WRONG — scenario says $0.00 but we're reusing the $120 stub; scenario not actually supported
self.given_payment_gateway_stubbed("120.00 AUD", {"status": "approved"})  # wrong amount
```

Do **not** assert what the stub returns as a THEN outcome — stub responses are preconditions, not business results:

```python
# WRONG — asserting the stub value, not the business outcome
assert result["transaction_id"] == "TXN-9912"   # this is infrastructure detail
# CORRECT — assert the business outcome instead
self.then_order_status_is(result, "Paid")
```

## Stub interaction structure in tests

Mirror the spec's GIVEN/WHEN/THEN stub pattern:

- **`given_*` helper**: configure the stub (request + hardcoded response).
- **`when_*` helper**: trigger the system action — the system will call the stub internally.
- **`then_*` helper**: assert the business outcome, not the stub response.

The stub invocation and its return happen **inside** `when_*` as side effects of the production code. They are never split across separate `when_*` and `then_*` calls.

```python
# CORRECT — stub fires inside when_*, then_ checks business result
def test_session_created_after_identity_check(self):
    self.given_identity_service_stubbed("tok-abc", {"user_id": "U-44", "roles": ["member"]})
    result = self.when_sign_in_processes_token("tok-abc")
    self.then_session_created_for(result, user_id="U-44")

# WRONG — exposing the stub's return as a when/then step
def test_session_created_after_identity_check(self):
    self.given_identity_service_stubbed("tok-abc", {"user_id": "U-44", "roles": ["member"]})
    response = self.when_identity_service_returns({"user_id": "U-44"})  # wrong — this is infrastructure
    self.then_session_created_for(response, user_id="U-44")
```
