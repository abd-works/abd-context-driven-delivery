---
scanner: ubiquitous_language_scanner.py
---

# Rule: Use Domain Language

Class names, file names, method names, and test names come from the **domain model** and **Gherkin scenarios** — not from technical patterns. When the story says "Recipient", the class is `Recipient`, the file is `Recipient.ts`, the collection is `Recipients`, and tests say "user views list of active recipients". Technical suffixes like `Manager`, `Handler`, `Processor`, `Helper`, or `Utility` hide domain intent and must be avoided on domain classes. Application services (the orchestration layer) may use the `Service` suffix.

## DO

- Name domain classes after domain nouns: `Recipient`, `BeneficiaryBank`, `RecipientSelection`.
- Name domain methods after domain verbs: `isEligibleForPayment()`, `filterByStatus()`, `placeOrder()`.
- Name files to match the domain concept: `Recipient.ts`, `RecipientStatus.ts`, `recipient.schema.ts`.
- Name test methods to mirror Gherkin scenarios verbatim: `test_user_views_list_of_active_recipients`.
- Use the `Service` suffix only for application-layer orchestrators: `RecipientsService`.
- Use server-tier naming conventions: `{domain}.routes.ts`, `{domain}.controller.ts`, `{domain}.repository.ts`.

```typescript
// CORRECT: domain class named after the domain concept
export class RecipientSelection {
  getEligibleForPayment(): Recipient[] { ... }
  filterByBankType(type: 'domestic' | 'international'): Recipient[] { ... }
}

// CORRECT: test name mirrors the Gherkin scenario
test('user views list of active recipients when initiating wire payment', async () => {
  await helper.givenEnterpriseHasRecipientsWithActiveStatus();
  await helper.whenUserInitiatesWirePayment();
  await helper.thenOnlyActiveRecipientsDisplayed();
});
```

## DON'T

- Use `Manager`, `Handler`, `Processor`, `Helper`, `Utility`, `Utils` on domain classes.
- Use generic names that hide domain meaning: `DataProcessor`, `ItemHandler`, `EntityManager`.
- Name test methods with technical jargon instead of scenario language.
- Use abbreviations that obscure domain concepts: `RecSel`, `BenBank`, `pymtCtrl`.

```typescript
// WRONG: technical suffixes hiding domain intent
export class RecipientManager { ... }      // What does "manage" mean in the domain?
export class PaymentProcessor { ... }      // Use the domain verb: Order.placeOrder()
export class BankDataHelper { ... }        // "Helper" is never a domain concept

// WRONG: test name uses technical language, not scenario language
test('GET /api/recipients returns 200 with filtered array', async () => { ... });
// CORRECT equivalent:
test('user views list of active recipients when initiating wire payment', async () => { ... });
```
