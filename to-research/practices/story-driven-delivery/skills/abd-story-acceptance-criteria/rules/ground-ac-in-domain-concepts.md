---
scanner: domain-grounded-ac
---

# Rule: Ground AC in domain concepts

**Scanner:** `scanners/domain-grounded-ac-scanner.py` — **`DomainGroundedACScanner`**

Every THEN, AND, and BUT must describe what is observable **using domain terms to classify what is shown, not just UI labels or generic nouns**. The reader must understand what kind of domain thing they are looking at — not just that something appears on screen.

## DO

- **Name the domain concept** that a displayed element represents. If the navigation shows links, say they are *services*. If a list shows rows, say what domain type each row is (a *recipient*, a *pending transaction*, etc.).
- **Use specific domain instances** rather than collapsing multiple named terms into a generic noun. Say "*available balance* and *book balance*" — not "balances" or "data".
- **Connect what's shown to domain relationships.** If a selector shows accounts, explain they are the *accounts* entitled under the *entitled accounts agreement*, not just "a list of accounts".
- **State observable outcomes** — what appears, what value a field displays, what control is enabled or disabled. The reader should be able to point at the screen and verify.
- When enumerating a set of fields or items, use the `·` separator and include the domain term that classifies the set (e.g. "each *recipient* row shows: profile name · *recipient* type").

## DON'T

- Use internal-action verbs as the observable outcome: "provides", "records", "sets", "triggers", "loads", "accepts", "processes". These describe what the system does internally — not what anyone can see.
- List UI labels without saying what domain concept they represent. "Shows links to Transaction Queue, Account Transfers, Tax Payments" is a label list. "Shows a link per entitled *service*: *ACH payments* · *account transfers* · *tax payments*" is domain-grounded.
- Collapse specific domain terms into generic nouns: "data", "balances", "details", "information", "items", "results". Always use the precise domain term.
- Describe navigation destinations by screen name alone when the domain term for what lives there is known.

## Examples

**Fail — label list, no domain grounding:**

```
THEN the drawer navigation shows links to Transaction Queue, Account Transfers,
     Recipient Management, ACH Payments, Tax Payments, and File Transfer
```

**Pass — domain-grounded:**

```
THEN the drawer navigation shows a link for each *service* the *finance user* is
     entitled to: *ACH payments* · *account transfers* · *tax payments* ·
     *file transfer* · *recipient management* — plus the *pending transaction* queue
```

**Fail — generic noun:**

```
THEN the daily cash position displays balance data for all accounts
```

**Pass — specific domain instances:**

```
THEN the *daily cash position* displays *available balance* and *book balance*
     per *account*
```

**Fail — internal-action verb:**

```
THEN the system records USD or CAD as the payment currency
```

**Pass — observable outcome with domain concept:**

```
THEN the Currency field displays the selected *currency* (USD or CAD)
```
