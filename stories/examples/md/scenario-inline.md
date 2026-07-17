---
fidelity: [specification]
artifact: [story-scenarios]
format: md
example-of: scenario-inline
---

<!-- Worked example — plain scenario with real domain values inline. -->
<!-- Shows the shape templates/md/scenario-inline.md produces once filled in. -->

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

### Evidence

| Scenario | Source (document / system) | Location |
| --- | --- | --- |
| Scenario 1 | *Payment Product Requirements* | §"Application flow", p. 12 |
| Scenario 2 | *Payment Product Requirements* | §"Rejection cases", p. 14 |
