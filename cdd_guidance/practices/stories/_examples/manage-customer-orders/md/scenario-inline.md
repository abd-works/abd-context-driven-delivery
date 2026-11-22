---
fidelity: [specification]
artifact: [story-scenarios]
format: md
example-of: scenario-template-inline
---

<!-- Worked example — plain scenario with real domain values inline. -->
<!-- Shows the alternate inline section of templates/md/scenario-template.md once filled in. -->

## Story: Apply For a Payment Product Agreement

**Story type:** user

### Domain terms

- *Customer* — account holder applying for the agreement
- *DDA Account* — demand deposit account; must be valid and eligible
- *Payment Product Agreement* — contract under review after submission
- *Owner* — named responsible party on the agreement
- *Contact Details* — email or phone used to notify the **Owner**

## Behaviors

### Scenario 1: Agreement submitted with valid DDA Account and Owner

*Given* a **Customer** *Jane Doe* exists  
  *And* that **Customer** *Jane Doe* has a valid **DDA Account** *DDA-001*  
*When* the **Customer** *Jane Doe* applies for a **Payment Product Agreement**  
    using **DDA Account** *DDA-001*  
    with **Owner** *John Doe*  
      that has **Contact Details** *john@acme.com*  
*Then* the **Payment Product Agreement** is submitted for review  
  *And* the **Owner** *John Doe* is notified at *john@acme.com*  

### Scenario 2: Agreement rejected when DDA Account is invalid

*Given* a **Customer** *Jane Doe* exists  
  *And* that **Customer** *Jane Doe* has **DDA Account** *DDA-999* with status *Invalid*  
*When* the **Customer** *Jane Doe* applies for a **Payment Product Agreement**  
    using **DDA Account** *DDA-999*  
*Then* the **Payment Product Agreement** is *rejected*  
  *And* **Customer** *Jane Doe* is notified that the **DDA Account** is *not eligible*  

### Edge conditions

| Edge condition | Scenario, "does not apply, because ...", or question for the person |
| --- | --- |
| Missing or empty input | Question for the person: the requirements name the **Owner** as required and do not say what the **Customer** sees when none is given. |
| Malformed input, or input at or past a limit | Scenario 2 covers a **DDA Account** that is not valid. Question for the person: is an **Owner**'s **Contact Details** checked for its form before the agreement is submitted? |
| Duplicate | Question for the person: may a **Customer** apply again with a **DDA Account** that already has a **Payment Product Agreement** under review? |
| Repeated action | Question for the person: the same question as Duplicate, for a **Customer** who submits the same application twice. |
| Two actors at once | Does not apply, because only the **Customer** who holds the **DDA Account** can apply with it (*Payment Product Requirements*, §"Application flow", p. 12). |
| Interrupted action | Question for the person: when the application stops before the **Owner** is notified, is the agreement still submitted for review? |
| Dependency absent, unavailable, slow, or wrong | Question for the person: what does the **Customer** see when the **DDA Account** cannot be checked? |
| Changed or gone since last seen | Scenario 2 covers a **DDA Account** whose status is *Invalid* when the application arrives, whatever it was when the **Customer** last saw it. |
| Actor not allowed | Does not apply, because the story opens with a signed-in **Customer** and the requirements give no other actor this action (§"Application flow", p. 12). |

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | *Payment Product Requirements* | §"Application flow", p. 12 |
| Scenario 2 | *Payment Product Requirements* | §"Rejection cases", p. 14 |
