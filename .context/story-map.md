---
fidelity: [discovery]
artifact: [story-map]
format: md
section: body
---

# Story Map — Paradise Mobile

**Sources / context:** System Landscape Overview (2026-08-24); `.context/bounded-context-map.md`

---

(E) Subscribe to Mobile Service
    **Sources / context:** My Paradise digital onboarding; DEP subscription catalog; Vouchera subscription-level vouchers; Cognito pool 2 via mid tier
    (E) Discover and Select Plan
        (S) Prospect --> Browse Subscription Catalog
        (S) Prospect --> Select Plan
        (S) Prospect --> Apply Subscription Voucher
    (E) Choose Number and SIM
        (S) Prospect --> Select New Telephone Number
        (S) Prospect --> Port Existing Telephone Number
        (S) Prospect --> Select SIM Type
    (E) Verify Identity and Complete Checkout
        (S) Prospect --> Verify Identity
        (S) Prospect --> Enter Billing Details
        (S) Prospect --> Complete Subscription Checkout
        (S) System --> Provision Subscriber Account

(E) Buy a Device
    **Sources / context:** Zoho Inventory Manager; Figaro and Vireo billing; payer ≠ subscriber gap; no DEP sync today
    (E) Purchase Without Subscription
        (S) Shopper --> Browse Device Catalog
        (S) Shopper --> Add Device To Cart
        (S) Payer --> Enter Payment Details
        (S) Payer --> Complete Device Purchase
    (E) Purchase With Different Payer and Subscriber
        (S) Payer --> Designate Subscription Beneficiary
        (S) Payer --> Complete Device Purchase For Beneficiary
        (S) System --> Record Payer Separately From Subscriber

(E) Manage Subscription and Billing
    **Sources / context:** My Paradise self-care; DEP as source of truth for subscriptions and billing
    (E) View Account and Usage
        (S) Subscriber --> View Dashboard
        (S) Subscriber --> View Data Usage
        (S) Subscriber --> View Latest Invoice
    (E) Change Subscription
        (S) Subscriber --> Change Plan
        (S) Subscriber --> Port Telephone Number
        (S) Subscriber --> Update Contact Details
    (E) Manage Payments
        (S) Subscriber --> Update Payment Method
        (S) Subscriber --> Pay Outstanding Invoice

(E) Redeem Promotion or Voucher
    **Sources / context:** Vouchera in DEP; customer-level affiliate codes; N8N volume discount automation
    (E) Apply Customer-Level Voucher
        (S) Customer --> Enter Affiliate Code
        (S) System --> Validate Affiliate Code
        (S) System --> Apply Volume Discount
    (E) Apply Cart-Level Voucher
        (S) Prospect --> Enter Promotional Code At Checkout
        (S) System --> Apply Cart Discount

(E) Get Customer Support
    **Sources / context:** Zendesk case management; customer profile from DEP; social channels (Facebook, LinkedIn, Instagram)
    (E) Raise Support Case
        (S) Customer --> Submit Support Request
        (S) Customer --> Submit Social Channel Message
        (S) System --> Create Support Case From Social Inbound
    (E) Track Support Case
        (S) Customer --> View Case Status
        (S) Agent --> Update Case Status
        (S) Agent --> Add Case Comment

(E) Receive Phone Support
    **Sources / context:** 3CX PBX integrated with Zendesk; phone lookup by number; transcription and sentiment opportunity
    (E) Handle Inbound Call
        (S) Caller --> Place Inbound Call
        (S) System --> Look Up Customer By Phone Number
        (S) System --> Open Existing Support Case
        (S) System --> Create Support Case For Unknown Caller
    (E) Enrich Call With Transcription
        (S) System --> Transcribe Inbound Call
        (S) System --> Attach Transcript To Support Case
        (S) System --> Summarize Call Sentiment

(E) Engage With Marketing Campaign
    **Sources / context:** Zoho Marketing Suite consolidation; Mailchimp, Typeforms, Zapier retiring; Juliano owns stack
    (E) Capture Lead
        (S) Visitor --> Complete Marketing Form
        (S) System --> Record Lead
    (E) Receive Campaign Communication
        (S) Lead --> Receive Campaign Email
        (S) Lead --> Follow Campaign Deep Link

---

## Scope boundary

**In scope:** Seven customer journeys mapped to current system interactions — subscribe, buy device, manage subscription, redeem voucher, get support, receive phone support, engage with marketing. Current-state mechanics reflected (manual data entry, orphan device commerce, DEP as subscription truth).

**Out of scope:** Back-office integration routing detail (Leo follow-up); marketing tool retirement sequence (Juliano follow-up); target-state architecture; building blocks and acceptance tests; internal admin and store operations (Cognito pool 1).

---

## Thin slices

### Increment 1: Answer "did Jeff buy a phone?"

**Outcome:** A support agent or system can correlate a customer across DEP subscription data and device commerce by email without manual cross-referencing four systems.

**Stories:**
- Complete Subscription Checkout (establishes DEP account as truth)
- Complete Device Purchase (records sale with payer email)
- Look Up Customer By Phone Number (support correlation entry point)

### Increment 2: Consistent customer entry at first touch

**Outcome:** Customer data entered once at onboarding propagates to Zendesk automatically; no fat-fingered duplicate "Jeffs."

**Stories:**
- Complete Subscription Checkout
- Provision Subscriber Account
- Create Support Case From Social Inbound (reuses DEP-sourced identity)

### Increment 3: Self-care without calling support

**Outcome:** Active subscriber can view usage, pay invoices, and change plan through My Paradise without agent intervention.

**Stories:**
- View Dashboard
- View Data Usage
- Change Plan
- Pay Outstanding Invoice

### Increment 4: Promotional sign-up with voucher

**Outcome:** Prospect applies a campaign voucher at sign-up and receives the discounted subscription price in DEP.

**Stories:**
- Apply Subscription Voucher
- Complete Subscription Checkout
- Provision Subscriber Account

### Increment 5: Phone support with context

**Outcome:** Inbound caller is recognized by phone number; agent sees existing Zendesk case history without asking Jeff to repeat himself.

**Stories:**
- Look Up Customer By Phone Number
- Open Existing Support Case
- Add Case Comment

### Increment 6: Device purchase with separate payer

**Outcome:** Payer and subscriber are formally recorded when Jeff pays for Mila's phone — foundation for cross-system correlation.

**Stories:**
- Designate Subscription Beneficiary
- Complete Device Purchase For Beneficiary
- Record Payer Separately From Subscriber

### Increment 7: Enriched phone support (opportunity)

**Outcome:** Inbound call is transcribed and summarized with sentiment; agent receives enriched ticket on answer.

**Stories:**
- Transcribe Inbound Call
- Attach Transcript To Support Case
- Summarize Call Sentiment

---

## Current vs target system interactions

| Journey | Current state | Target state (themes) |
|---|---|---|
| Subscribe | My Paradise → mid tier → DEP; manual gaps in CRM/Zoho | Single customer entry; DEP truth propagates downstream |
| Buy device | Zoho Inventory manual; no DEP sync; payer ≠ subscriber ad hoc | Formal payer/subscriber model; chosen cart strategy (DEP vs Zoho vs custom) |
| Manage subscription | My Paradise self-care via mid tier → DEP | unchanged seam; reduce duplicate CRM entry |
| Redeem voucher | Vouchera in DEP; N8N for affiliate volume | cart-level vouchers when shopping cart strategy decided |
| Get support | Zendesk from DEP trigger; social inbound; manual profile | consistent identity from DEP; no duplicate customer creation |
| Phone support | 3CX lookup → Zendesk ticket; no transcription | auto-transcription and sentiment on ticket generation (Samir) |
| Marketing | Tool sprawl (Mailchimp, Typeforms, Zapier, spreadsheets) | Zoho Marketing Suite consolidation (Juliano) |
