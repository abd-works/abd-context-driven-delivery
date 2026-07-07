---
fidelity: [exploration, specification, engineering]
artifact: [ac, scenario, test]
scanner: emphasise-domain-terms
kind: quality

---

# Rule: Emphasise Domain-Significant Terms

Call out domain language — nouns, verbs, and short phrases from the problem space — so readers see what is specific to this product versus generic wording.

## DO

- Wrap domain-significant terms in **bold** in step lines
- Use *italic* for values/instances of those concepts
- Apply consistently for the same concept across all steps in a story
- Multi-word concepts use Title Case: **Payment Product Agreement**, **DDA Account**

## DON'T

- Italicise/bold entire sentences or filler words
- Use emphasis as decoration — only terms that carry domain meaning
- Collapse specific domain terms into generic nouns (`data`, `details`, `items`)

## At each fidelity

**Exploration — AC steps:**
```
When the **Customer** submits a **Payment Product Agreement**
  using **DDA Account** *DDA-001*
Then the **Payment Product Agreement** is *submitted for review*
```

**Specification — scenario steps and table column names:**
```
Given a **Customer** *Jane Doe* with **DDA Account** *DDA-001*
When the **Customer** applies for a **Payment Product Agreement**
Then the **Payment Product Agreement** status is *Submitted*
```
Column names in example tables use snake_case of the domain term:
`payment_product_agreement_id`, `dda_account_id`

**Engineering — class, method, and variable names:**
```python
payment_product_agreement = given_payment_product_agreement(customer=jane_doe)
when_customer_applies(customer=jane_doe, account=dda_001)
assert payment_product_agreement.status == "Submitted"
```
