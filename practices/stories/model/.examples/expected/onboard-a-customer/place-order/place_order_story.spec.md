---
fidelity: [scenarios]
artifact: [story-scenarios]
format: md
---

# Epic: Place Order

Collapsed from hop-level system stories into the story-map domain operations. Actor is **Customer**. Done-page copy is UX — stories assert domain state (`orderSuccess`, `payUpFront`, `verified`, sim / iccid).

**Sources**

- `pml-my/src/pages/Onboarding/pages/Checkout/steps/Payment/hooks/usePayment.tsx` L73–111 (`createOrder`: billing then order, then `defaultPayment` / `verified` / navigate)
- `pml-midtier/src/entities/Mavenir/controllers/customer/controller.ts` L180–205 (`createBilling`), L362–511 (`createOrder`), L743–809 (`preCookOrder`, `cookOrder`), L255–304 (`zendeskTicketOrder`)
- `pml-midtier/src/services/Zendesk/zendesk.service.ts` · `config.ts` (ticket subjects)
- `pml-my/src/pages/Onboarding/pages/Done/Done.tsx` (`allSet = success && payUpFront && verified && (eSIM || pSIM+iccid)`)

## Examples

| billing account | example | id |
| --- | --- | --- |
| billing account | new billing account | from billingAccount |

| product order | example | id |
| --- | --- | --- |
| product order | new product order | from productOrderFromCart |

| Zendesk ticket | example | subject |
| --- | --- | --- |
| Zendesk ticket | ID ticket | ID Verification Required |
| Zendesk ticket | pSIM ticket | SIM Delivery Required |
| Zendesk ticket | ID and pSIM ticket | ID Verification Required and SIM Delivery Required |
| Zendesk ticket | trial ticket | Promotional trial |
| Zendesk ticket | portability ticket | Portability Required |
| Zendesk ticket | pay-up-front failed ticket | Payment failed |
| Zendesk ticket | roaming ticket | Roaming plan - New Subscription |

---

## Story: Create Billing Account

**Story type:** My Paradise

### Background

*Given* the Customer has a configured cart  
  *But* the Customer has no billing account

### Scenario: Create billing account

*When* the Customer creates a billing account  
*Then* My Paradise sends the billing account request to Mavenir  
*When* Mavenir creates the billing account  
*Then* the Customer has a billing account  
  *And* the Customer is on the Done step

### Scenario: Billing account already exists

*Given* the Customer already has a billing account  
*When* the Customer creates a billing account  
*Then* the billing account is rejected  
  *And* Mavenir does not receive a billing account request

### Scenario: Billing account creation fails

*Given* Mavenir returns an error for the billing account request  
*When* the Customer creates a billing account  
*Then* the billing account cannot be created  
  *And* the Customer has no billing account

---

## Story: Create Product Order

**Story type:** My Paradise

Pay-up-front and roaming are Given preconditions on the order path.

### Background

*Given* the Customer has a billing account  
  *And* the cart has plan, number, and SIM

### Scenario: Create product order

*Given* the Customer is verified  
*When* the Customer places the product order  
*Then* My Paradise sends the product order request to Mavenir  
*When* Mavenir creates the product order  
*Then* the order succeeded with pay-up-front  
  *And* the Customer onboarding is done

### Scenario: Pay-up-front charge fails

*Given* the pay-up-front charge fails  
*When* the Customer places the product order  
*Then* My Paradise does not send a product order to Mavenir  
  *And* the order succeeded without pay-up-front

### Scenario: Product order fails

*Given* Mavenir returns an error for the product order  
*When* the Customer places the product order  
*Then* the order did not succeed

### Scenario: Onboarding is already done

*Given* the Customer onboarding is already done  
*When* the Customer places the product order  
*Then* the product order is rejected  
  *And* Mavenir does not receive a product order request

### Scenario: Unverified with no bypass and no portability

*Given* the Customer is not verified  
  *And* the plan does not bypass verification  
  *And* the cart has no portability  
*When* the Customer places the product order  
*Then* My Paradise does not send a product order to Mavenir  
  *And* the cart is marked to submit the order later  
  *And* the Customer onboarding is done

---

## Story: View Order Result

**Story type:** My Paradise

### Scenario Outline: View order result

*Given* the order result is {example}  
*When* the Customer views their order result  
*Then* the order is {outcome}

| example | success | payUpFront | verified | sim | outcome |
| --- | --- | --- | --- | --- | --- |
| verified eSIM | true | true | true | eSIM | complete |
| verified pSIM with ICCID | true | true | true | pSIM + ICCID | complete |
| unverified | true | true | false | eSIM | not yet complete |
| verified pSIM without ICCID | true | true | true | pSIM | not yet complete |
| pay-up-front failed | true | false | true | eSIM | not yet complete |
| order failed | false | | true | eSIM | not yet complete |

---

## Story: Create Order Ticket

**Story type:** My Paradise

Create Order Ticket is a My Paradise operation that invokes Zendesk. Hops are when/then pairs.

### Scenario Outline: Create order ticket

*Given* the Customer {example}  
*When* the Customer creates the order ticket  
*Then* My Paradise sends the {subject} ticket to Zendesk  
*When* Zendesk creates the ticket  
*Then* the ticket is created for the Customer

| example | subject |
| --- | --- |
| unverified eSIM | ID Verification Required |
| verified pSIM without ICCID | SIM Delivery Required |
| unverified pSIM without ICCID | ID Verification Required and SIM Delivery Required |
| trial voucher | Promotional trial |
| unverified portability | Portability Required |
| pay-up-front charge failed | Payment failed |
| roaming plan | Roaming plan - New Subscription |

---

## Story: View Order History

**Story type:** Care

**Intended GWT only.** DEP Order History is Mavenir DEP UI — no code path in `pml-my` or `pml-midtier`. Observed in granola `23-dep-order-history.png`. Status badges can lag after My Paradise places the order.

### Background

*Given* the Customer has a product order in Mavenir  
  *And* Care is in Customer Management → Order History

### Scenario: View Order History

*When* Care views Order History for the Customer  
*Then* Care sees the product order with status badges
