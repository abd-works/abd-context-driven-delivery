---
fidelity: [shaping, discovery, exploration, specification, engineering]
artifact: [story-map, ac, scenario, test]
scanner: behavioral-observable-outcomes
kind: quality

---

# Rule: Behavioral Observable Outcomes

Every artifact — outcome name, activity name, story name, `Then` step, `And` step, `But` step, and assertion — must describe **what is observable** in domain terms. What a user or system can see or verify. Never describe internal mechanics.

This is the single spine that runs from the outcome label at the top of the story map down to the final `assert` in a test. Same rule, different words per fidelity.

## DO

- State what is **shown**, **displayed**, **available**, **marked as**, **created**, **received**
- Name the domain concept that a displayed element represents
- Use specific domain instances (`available balance`), not generic nouns (`balance data`)
- Connect what is shown to domain relationships (which Actor sees it, which Entity holds it)

## DON'T

- Use internal-action verbs: `records`, `triggers`, `sets`, `loads`, `accepts`, `processes`, `handles`, `manages`
- List UI labels without stating what domain concept they represent
- Collapse domain terms into generic nouns: `data`, `details`, `information`, `results`
- Assert on private attributes or internal state in tests

## At each fidelity

**Shaping — outcome names:**
```
Wrong — internal / vague
- Payment System
- Manage payments
- Data ingestion

Correct — observable business outcome
- Payments moved between Accounts
- Overdue Payments cleared
- Reconciled statement delivered to Customer
```

**Shaping — activity names:**
```
Wrong — internal action / verb + system noun
- Process payment
- Handle refund
- Load statement

Correct — observable user or business activity (verb + domain noun)
- Submit payment
- Approve refund
- Review statement
```

**Discovery — story names:**
```
Wrong — mixes internal and observable
- Payment processor validates account

Correct — observable actor + observable outcome
- Customer submits payment from savings account
- System rejects payment when daily limit exceeded
```

**Exploration — AC Then steps:**
```
Wrong — internal action
Then the system records the Payment Product Agreement

Correct — observable outcome
Then the Payment Product Agreement status is Submitted for Review
And the Owner is notified at their Contact Details email
```

**Specification — scenario Then steps:**
```
Wrong — internal state
Then agreement.status is set to SUBMITTED

Correct — observable domain outcome
Then the **Payment Product Agreement** {agreement_id} has status *Submitted*
And **Owner** {owner_id} receives notification at {owner_email}
```

**Engineering — assertions:**
```python
# Wrong — internal state
assert agreement._status == "SUBMITTED"

# Correct — public observable outcome
assert agreement.status == "Submitted"
assert owner.notification_sent_to == owner_email
```

## Cross-references

- `verb-noun-format.md` — the naming shape this rule sits on top of
- `vocabulary-traces-to-domain-source.md` — the domain terms used here must trace to a source
- `scenario-step-quality.md` — the step-quality rule that enforces this at the sentence level for scenarios
